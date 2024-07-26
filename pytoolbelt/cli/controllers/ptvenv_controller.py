import shutil

from semver import Version

from pytoolbelt.cli.controllers.common import release
from pytoolbelt.core.data_classes.component_metadata import ComponentMetadata
from pytoolbelt.core.data_classes.pytoolbelt_config import PytoolbeltConfig
from pytoolbelt.core.data_classes.toolbelt_config import ToolbeltConfig
from pytoolbelt.core.error_handling.exceptions import PytoolbeltError
from pytoolbelt.core.project.ptvenv_components import (
    PtVenvBuilder,
    PtVenvConfig,
    PtVenvPaths,
    PtVenvTemplater,
)
from pytoolbelt.core.project.toolbelt_components import ToolbeltPaths
from pytoolbelt.core.tools import hash_config
from pytoolbelt.core.tools.git_client import TemporaryGitClient
from pytoolbelt.environment.config import get_logger

logger = get_logger(__name__)

"""
    TODO: This controller's constructors are quite similar to that of the tool controller. 
    this should be reviewed as a good candidate for DRY out refactoring.
"""


class PtVenvController:
    def __init__(self, meta: ComponentMetadata, toolbelt: ToolbeltConfig, **kwargs) -> None:
        self.meta = meta
        self.toolbelt = toolbelt
        self.toolbelt_paths = kwargs.get("toolbelt_paths", ToolbeltPaths(toolbelt.path))
        self.ptvenv_paths = kwargs.get("paths", PtVenvPaths(meta, self.toolbelt_paths))

    @classmethod
    def for_creation(cls, string: str, toolbelt: ToolbeltConfig) -> "PtVenvController":
        version = Version.parse("0.0.1")
        meta = ComponentMetadata.as_ptvenv(string, version)
        logger.debug(f"Creating ptvenv controller for_creation for {meta.name} with version {meta.version}.")
        return cls(meta, toolbelt)

    @classmethod
    def for_deletion(cls, string: str, toolbelt: ToolbeltConfig) -> "PtVenvController":
        meta = ComponentMetadata.as_ptvenv(string)
        inst = cls(meta, toolbelt)

        if not inst.meta.is_latest_version:
            logger.debug(
                f"Creating ptvenv controller for_deletion of ptvenv {inst.meta.name} version {inst.meta.version}."
            )
            return inst

        latest_version = inst.ptvenv_paths.get_latest_installed_version()
        inst.meta.version = latest_version
        logger.debug(f"Creating ptvenv controller for_deletion of ptvenv {inst.meta.name} version {inst.meta.version}.")
        return inst

    @classmethod
    def for_release(cls, string: str, toolbelt: ToolbeltConfig) -> "PtVenvController":
        meta = ComponentMetadata.as_ptvenv(string)
        inst = cls(meta, toolbelt)

        # we passed in some type of version in the format name==version and this
        # is not allowed, when making a release.
        if isinstance(meta.version, Version):
            raise PytoolbeltError(f"Setting a version number is not allowed when releasing a ptvenv.")

        # otherwise get the latest version number from the config file
        config = PtVenvConfig.from_file(inst.ptvenv_paths.ptvenv_config_file)
        inst.meta.version = config.version
        logger.debug(f"Creating ptvenv controller for_release of ptvenv {inst.meta.name} version {inst.meta.version}.")
        return inst

    @classmethod
    def for_build(cls, string: str, toolbelt: ToolbeltConfig) -> "PtVenvController":
        meta = ComponentMetadata.as_ptvenv(string)
        inst = cls(meta, toolbelt)

        # this means we passed in some version number in the format name==version
        if isinstance(meta.version, Version):
            logger.debug(
                f"Creating ptvenv controller for_build of ptvenv {inst.meta.name} passed in version {inst.meta.version}."
            )
            return inst

        # this means we are building, or releasing a new / latest version,
        config = PtVenvConfig.from_file(inst.ptvenv_paths.ptvenv_config_file)
        inst.meta.version = config.version
        logger.debug(f"Creating ptvenv controller for_build of ptvenv {inst.meta.name} version {inst.meta.version}.")
        return inst

    def get_templater(self) -> PtVenvTemplater:
        return PtVenvTemplater(self.ptvenv_paths)

    def get_builder(self) -> PtVenvBuilder:
        return PtVenvBuilder(self.ptvenv_paths)

    def create(self, ptc: PytoolbeltConfig) -> int:
        self.toolbelt_paths.raise_if_not_pytoolbelt_project()
        self.ptvenv_paths.raise_if_exists()
        self.ptvenv_paths.create()
        self.get_templater().template_new_venvdef_file(ptc=ptc)
        logger.info(
            f"Ptvenv {self.meta.name} created in toolbelt {self.toolbelt.name} at {self.ptvenv_paths.ptvenv_dir}."
        )
        return 0

    def build(self, force: bool, from_config: bool) -> int:
        # TODO: This can be DRYed out with the tool controller...

        logger.info(f"Building {self.meta.name} version {self.meta.version} in {self.toolbelt.name}.")

        with TemporaryGitClient(self.toolbelt.path, self.toolbelt.name) as (repo_path, git_client):

            logger.debug(f"toolbelt copied to temp dir:  {repo_path.tmp_dir}")

            # if we have uncommitted changes and are not installing from the file, raise an error
            if not from_config and not force:
                git_client.raise_if_uncommitted_changes()

            # if we are installing from file and not forcing, then check if the installation can proceed
            # otherwise, just run the builder and install what is in the file.
            if from_config:

                # only check the config / installed hash if we are not forcing the build
                if not force:
                    ptvenv_config = PtVenvConfig.from_file(self.ptvenv_paths.ptvenv_config_file)
                    self._installation_can_proceed(ptvenv_config)

                # run the builder for this ptvenv
                self.get_builder().build()
                return 0

            # if we did not pass in a version in the cli, and we are not installing from file, this means
            # we need to get the latest release from the repo, and create the metadata.
            elif self.ptvenv_paths.meta.is_latest_version:
                tags = git_client.ptvenv_releases(name=self.meta.name, as_names=True)
                latest_meta = ComponentMetadata.get_latest_release(tags)

            # in all other cases, this means we passed in a version in the cli,
            # so just go with whatever was passed in.
            else:
                latest_meta = self.meta

            # get the tag reference for the latest release. If it is not found
            # in the repo, we will raise an error and exit as we don't know what to install.
            try:
                tag_reference = git_client.get_tag_reference(latest_meta.release_tag)
            except IndexError:
                raise PytoolbeltError(f"Version {self.meta.version} not found in the repository.")

            # check out from the release tag in the temp repo
            logger.debug(f"Checking out tag {tag_reference}")
            git_client.checkout_tag(tag_reference)

            # create new paths and builder pointed to the temp repo
            tmp_project_paths = ToolbeltPaths(repo_path.tmp_dir)
            tmp_paths = PtVenvPaths(latest_meta, tmp_project_paths)

            if not force:
                tmp_ptvenv_config = PtVenvConfig.from_file(tmp_paths.ptvenv_config_file)
                self._installation_can_proceed(tmp_ptvenv_config)

            tmp_builder = PtVenvBuilder(tmp_paths)
            logger.info(f"Building {latest_meta.name} version {latest_meta.version} in {self.toolbelt.name}.")
            tmp_builder.build()
            logger.info(f"Built {latest_meta.name} version {latest_meta.version} in {self.toolbelt.name} successfully.")
            return 0

    def _installation_can_proceed(self, current_config: PtVenvConfig) -> None:
        # the installation directory exists, so we need to check if the configuration has changed
        # if it has, we need to warn the user that the environment definition has changed, however
        # the version has not been updated. This could lead to unexpected behavior.
        if self.ptvenv_paths.install_dir.exists():

            installed_config = PtVenvConfig.from_file(self.ptvenv_paths.installed_config_file)

            hashed_current_config = hash_config(current_config)
            hashed_installed_config = hash_config(installed_config)

            installed_hash = self.ptvenv_paths.installed_hash_file.read_text()

            # this means that the installation file has been messed with, so we need to rebuild the environment
            if installed_hash != hashed_installed_config:
                raise PytoolbeltError(
                    f"Warning 1: ptvenv definition for {self.meta.name} version {self.meta.version} has been modified since install. "
                    f"Please run 'ptvenv build --force' to rebuild the environment. This will replace {self.meta.name} version {self.meta.version} with the new version definition."
                )

            if hashed_current_config != hashed_installed_config:
                raise PytoolbeltError(
                    f"Warning 2: ptvenv definition for {self.meta.name} version {self.meta.version} has changed since install. "
                    f"Please run 'ptvenv build --force' to rebuild the environment. This will replace {self.meta.name} version {self.meta.version} with the new version definition."
                )

            if hashed_current_config == hashed_installed_config:
                raise PytoolbeltError(
                    f"Python environment {self.meta.name} version {self.meta.version} is already up to date."
                )

    def delete(self, _all: bool) -> int:
        if self.ptvenv_paths.install_dir.exists():
            if _all:
                logger.info(f"Deleting all ptvenv installations for {self.meta.name}.")
                shutil.rmtree(self.ptvenv_paths.install_root_dir)
            else:
                logger.info(f"Deleting ptvenv {self.meta.name} version {self.meta.version}.")
                shutil.rmtree(self.ptvenv_paths.install_dir.parent)
            return 0
        else:
            raise PytoolbeltError(f"ptvenv {self.meta.name} version {self.meta.version} is not installed.")

    def bump(self, ptc: PytoolbeltConfig, part: str) -> int:
        logger.info(f"Bumping version of ptvenv {self.meta.name} in toolbelt {self.toolbelt.name}.")
        if part == "config":
            part = ptc.bump

        config = PtVenvConfig.from_file(self.ptvenv_paths.ptvenv_config_file)
        next_version = self.ptvenv_paths.meta.version.next_version(part)
        config.version = next_version
        self.ptvenv_paths.write_to_config_file(config)
        logger.info(f"Ptvenv {self.meta.name} bumped to version {next_version}.")
        return 0

    def release(self, ptc: PytoolbeltConfig) -> int:
        logger.info(f"Releasing ptvenv {self.meta.name} in toolbelt {self.toolbelt.name}.")
        return release(ptc=ptc, toolbelt_paths=self.toolbelt_paths, component_paths=self.ptvenv_paths)
