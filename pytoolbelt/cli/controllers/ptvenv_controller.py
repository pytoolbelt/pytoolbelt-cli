import shutil
import tempfile
from pathlib import Path
from typing import Optional

from semver import Version

from pytoolbelt.cli.controllers.common import release
from pytoolbelt.cli.views.ptvenv_views import (
    PtVenvInstalledTableView,
    PtVenvReleasesTableView,
)
from pytoolbelt.core.data_classes.component_metadata import ComponentMetadata
from pytoolbelt.core.data_classes.pytoolbelt_config import PytoolbeltConfig
from pytoolbelt.core.data_classes.toolbelt_config import ToolbeltConfig, ToolbeltConfigs
from pytoolbelt.core.error_handling.exceptions import (
    CreateReleaseError,
    PtVenvCreationError,
    PtVenvNotFoundError,
)
from pytoolbelt.core.project.ptvenv_components import (
    PtVenvBuilder,
    PtVenvConfig,
    PtVenvPaths,
    PtVenvTemplater,
)
from pytoolbelt.core.project.toolbelt_components import ToolbeltPaths
from pytoolbelt.core.tools import hash_config
from pytoolbelt.core.tools.git_client import GitClient, TemporaryGitClient
from pytoolbelt.environment.config import PYTOOLBELT_TOOLBELT_ROOT

"""
    TODO: This controller's constructors are quite similar to that of the tool controller. 
    this should be reviewed as a good candidate for DRY out refactoring.
"""


class PtVenvController:
    def __init__(self, meta: ComponentMetadata, root_path: Optional[Path] = None, **kwargs) -> None:
        self.toolbelt_paths = kwargs.get("toolbelt_paths", ToolbeltPaths(root_path))
        self.paths = kwargs.get("paths", PtVenvPaths(meta, self.toolbelt_paths))
        self.templater = kwargs.get("templater", PtVenvTemplater(self.paths))
        self.builder = kwargs.get("builder", PtVenvBuilder(self.paths))

    @classmethod
    def from_ptvenv_paths(cls, paths: PtVenvPaths) -> "PtVenvController":
        return cls(paths.meta, paths.project_paths, paths=paths)

    @classmethod
    def for_creation(cls, string: str, root_path: Optional[Path] = None) -> "PtVenvController":
        version = Version.parse("0.0.1")
        meta = ComponentMetadata.as_ptvenv(string, version)
        return cls(meta, root_path)

    @classmethod
    def for_deletion(cls, string: str, root_path: Optional[Path] = None) -> "PtVenvController":
        meta = ComponentMetadata.as_ptvenv(string)
        inst = cls(meta, root_path)

        if not inst.paths.meta.is_latest_version:
            return inst

        latest_version = inst.paths.get_latest_installed_version()
        inst.paths.meta.version = latest_version
        return inst

    @classmethod
    def for_release(cls, string: str, root_path: Optional[Path] = None) -> "PtVenvController":
        meta = ComponentMetadata.as_ptvenv(string)
        inst = cls(meta, root_path)

        # we passed in some type of version in the format name==version and this
        # is not allowed, when making a release.
        if isinstance(meta.version, Version):
            raise CreateReleaseError(
                f"Cannot release ptvenv {inst.paths.meta.name} with version {inst.paths.meta.version} versions must be bumps in the ptvenv config file."
            )

        # otherwise get the latest version number from the config file
        config = PtVenvConfig.from_file(inst.paths.ptvenv_config_file)
        inst.paths.meta.version = config.version
        return inst

    @classmethod
    def for_build(cls, string: str, root_path: Optional[Path] = None) -> "PtVenvController":
        meta = ComponentMetadata.as_ptvenv(string)
        inst = cls(meta, root_path)

        # this means we passed in some version number in the format name==version
        if isinstance(meta.version, Version):
            return inst

        # this means we are building, or releasing a new / latest version,
        config = PtVenvConfig.from_file(inst.paths.ptvenv_config_file)
        inst.paths.meta.version = config.version
        return inst

    @classmethod
    def from_release_tag(cls, tag: str, root_path: Optional[Path] = None) -> "PtVenvController":
        meta = ComponentMetadata.from_release_tag(tag)
        return cls(meta, root_path)

    @property
    def release_tag(self) -> str:
        return self.paths.meta.release_tag

    def raise_if_exists(self) -> None:
        if self.paths.ptvenv_dir.exists():
            raise PtVenvCreationError(f"Python environment {self.paths.meta.name} already exists.")

    def raise_if_not_pytoolbelt_project(self) -> None:
        git_client = GitClient.from_path(self.toolbelt_paths.root_path)
        self.toolbelt_paths.raise_if_not_pytoolbelt_project(git_client.repo)

    def create(self, ptc: PytoolbeltConfig) -> int:
        self.raise_if_not_pytoolbelt_project()
        self.raise_if_exists()
        self.paths.create()
        self.templater.template_new_venvdef_file(ptc=ptc)
        return 0

    def build(self, force: bool, path: Path, toolbelt: str, from_config: bool) -> int:
        # TODO: This can be DRYed out with the tool controller...
        with TemporaryGitClient(path, toolbelt) as (repo_path, git_client):

            # if we have uncommitted changes and are not installing from the file, raise an error
            if not from_config and not force:
                git_client.raise_if_uncommitted_changes()

            # if we are installing from file and not forcing, then check if the installation can proceed
            # otherwise, just run the builder and install what is in the file.
            if from_config:

                # only check the config / installed hash if we are not forcing the build
                if not force:
                    ptvenv_config = PtVenvConfig.from_file(self.paths.ptvenv_config_file)
                    self._installation_can_proceed(ptvenv_config)

                # run the builder for this ptvenv
                self.builder.build()
                return 0

            # if we did not pass in a version in the cli, and we are not installing from file, this means
            # we need to get the latest release from the repo, and create the metadata.
            elif self.paths.meta.is_latest_version:
                tags = git_client.ptvenv_releases(name=self.paths.meta.name, as_names=True)
                latest_meta = ComponentMetadata.get_latest_release(tags)

            # in all other cases, this means we passed in a version in the cli,
            # so just go with whatever was passed in.
            else:
                latest_meta = self.paths.meta

            # get the tag reference for the latest release. If it is not found
            # in the repo, we will raise an error and exit as we don't know what to install.
            try:
                tag_reference = git_client.get_tag_reference(latest_meta.release_tag)
            except IndexError:
                raise PtVenvCreationError(f"Version {self.paths.meta.version} not found in the repository.")

            # check out from the release tag in the temp repo
            print(f"Checking out tag {tag_reference}")
            git_client.checkout_tag(tag_reference)

            # create new paths and builder pointed to the temp repo
            tmp_project_paths = ToolbeltPaths(repo_path.tmp_dir)
            tmp_paths = PtVenvPaths(latest_meta, tmp_project_paths)

            if not force:
                tmp_ptvenv_config = PtVenvConfig.from_file(tmp_paths.ptvenv_config_file)
                self._installation_can_proceed(tmp_ptvenv_config)

            tmp_builder = PtVenvBuilder(tmp_paths)
            print(f"Building {self.paths.meta.name} version {self.paths.meta.version} from {tag_reference}")
            tmp_builder.build()
            return 0

    def _installation_can_proceed(self, current_config: PtVenvConfig) -> None:
        # the installation directory exists, so we need to check if the configuration has changed
        # if it has, we need to warn the user that the environment definition has changed, however
        # the version has not been updated. This could lead to unexpected behavior.
        if self.paths.install_dir.exists():

            installed_config = PtVenvConfig.from_file(self.paths.installed_config_file)

            hashed_current_config = hash_config(current_config)
            hashed_installed_config = hash_config(installed_config)

            installed_hash = self.paths.installed_hash_file.read_text()

            # this means that the installation file has been messed with, so we need to rebuild the environment
            if installed_hash != hashed_installed_config:
                raise PtVenvCreationError(
                    f"Warning 1: ptvenv definition for {self.paths.meta.name} version {self.paths.meta.version} has been modified since install. "
                    f"Please run 'ptvenv build --force' to rebuild the environment. This will replace {self.paths.meta.name} version {self.paths.meta.version} with the new version definition."
                )

            if hashed_current_config != hashed_installed_config:
                raise PtVenvCreationError(
                    f"Warning 2: ptvenv definition for {self.paths.meta.name} version {self.paths.meta.version} has changed since install. "
                    f"Please run 'ptvenv build --force' to rebuild the environment. This will replace {self.paths.meta.name} version {self.paths.meta.version} with the new version definition."
                )

            if hashed_current_config == hashed_installed_config:
                raise PtVenvCreationError(
                    f"Python environment {self.paths.meta.name} version {self.paths.meta.version} is already up to date."
                )

    def delete(self, _all: bool) -> int:
        if self.paths.install_dir.exists():
            if _all:
                shutil.rmtree(self.paths.install_root_dir)
            else:
                shutil.rmtree(self.paths.install_dir.parent)
            return 0
        else:
            raise PtVenvNotFoundError(
                f"Python environment {self.paths.meta.name} version {self.paths.meta.version} is not installed."
            )

    def bump(self, part: str) -> int:
        config = PtVenvConfig.from_file(self.paths.ptvenv_config_file)
        next_version = self.paths.meta.version.next_version(part)
        config.version = str(next_version)
        self.paths.write_to_config_file(config)
        return 0

    def release(self, ptc: PytoolbeltConfig) -> int:
        return release(ptc=ptc, toolbelt_paths=self.toolbelt_paths, component_paths=self.paths)

    def releases(self, repo: str) -> int:
        repo_config = ToolbeltConfigs.load().get(repo)
        table = PtVenvReleasesTableView(repo_config)
        git_client = GitClient.from_path(self.toolbelt_paths.root_path)

        for tag in git_client.ptvenv_releases():
            meta = ComponentMetadata.from_release_tag(tag.name)
            table.add_row(meta.name, meta.version, str(tag.commit.committed_datetime.date()), tag.commit.hexsha)
        table.print_table()
        return 0

    def installed(self) -> int:
        table = PtVenvInstalledTableView()
        installed_ptvenvs = list(self.toolbelt_paths.iter_installed_ptvenvs())
        installed_ptvenvs.sort(key=lambda x: (x.version, x.name), reverse=True)
        for installed_ptvenv in installed_ptvenvs:
            ptvenv_paths = PtVenvPaths(installed_ptvenv, self.toolbelt_paths)
            table.add_row(installed_ptvenv.name, installed_ptvenv.version, ptvenv_paths.display_install_dir)
        table.print_table()
        return 0
