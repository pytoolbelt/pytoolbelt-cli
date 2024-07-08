import shutil
import tempfile
from pathlib import Path
from typing import Optional

from semver import Version
from pytoolbelt.core.data_classes.component_metadata import ComponentMetadata
from pytoolbelt.core.error_handling.exceptions import (
    PtVenvCreationError,
    PtVenvNotFoundError,
)
from pytoolbelt.core.tools import hash_config
from pytoolbelt.core.tools.git_client import GitClient
from pytoolbelt.cli.controllers.project_controller import Project
from pytoolbelt.environment.config import PYTOOLBELT_TOOLBELT_ROOT
from pytoolbelt.cli.views.ptvenv_views import PtVenvInstalledTableView, PtVenvReleasesTableView
from pytoolbelt.core.data_classes.pytoolbelt_config import PytoolbeltConfig
from pytoolbelt.core.project.toolbelt_components import ToolbeltPaths
from pytoolbelt.core.project.ptvenv_components import PtVenvBuilder, PtVenvConfig, PtVenvPaths, PtVenvTemplater
from pytoolbelt.core.data_classes.toolbelt_config import ToolbeltConfigs


class PtVenvController:
    def __init__(self, meta: ComponentMetadata, root_path: Optional[Path] = None, **kwargs) -> None:
        self.project_paths = kwargs.get("project_paths", ToolbeltPaths(root_path))
        self.paths = kwargs.get("paths", PtVenvPaths(meta, self.project_paths))
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
    def for_build_and_release(cls, string: str, root_path: Optional[Path] = None) -> "PtVenvController":
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
    def from_cli(
            cls,
            string: str,
            root_path: Optional[Path] = None,
            creation: Optional[bool] = False,
            deletion: Optional[bool] = False,
            build: Optional[bool] = False,
    ) -> "PtVenvController":
        meta = ComponentMetadata.as_ptvenv(string)
        inst = cls(meta, root_path)

        # this means it's the first time we're creating a ptvenv definition file
        # for the passed in name. So we set the version to 0.0.1
        if creation:
            inst.paths.meta.version = Version.parse("0.0.1")
            return inst

        if deletion:
            if isinstance(inst.paths.meta.version, str):
                if inst.paths.meta.version == "latest":
                    latest_installed_version = inst.paths.get_latest_installed_version()
                    inst.paths.meta.version = latest_installed_version
                return inst

        if build:
            # this means we are building, or releasing a new version,
            # and we passed in a version number in the format name==version
            if isinstance(meta.version, Version):
                return inst
            config = PtVenvConfig.from_file(inst.paths.ptvenv_config_file)
            inst.paths.meta.version = config.version
            return inst

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

    def create(self, ptc: PytoolbeltConfig) -> int:
        self.raise_if_exists()
        self.paths.create()
        self.templater.template_new_venvdef_file(ptc=ptc)
        return 0

    def build(self, force: bool) -> int:
        ptvenv_config = PtVenvConfig.from_file(self.paths.ptvenv_config_file)

        # this means we passed in some version number in the format name==version
        # we need to get the current tags from the repo, if a suitable tag is found
        # we need to copy the entire repo to a temp dir, and check out the tag.
        # we can then install the environment from the temp dir, but we must construct new PtVenvPaths and a builder.
        if ptvenv_config.version != self.paths.meta.version:
            git_client = GitClient.from_path(self.project_paths.root_path)

            try:
                tag_reference = git_client.get_tag_reference(self.paths.meta.release_tag)
            except IndexError:
                raise PtVenvCreationError(f"Version {self.paths.meta.version} not found in the repository.")

            with tempfile.TemporaryDirectory() as tmp_dir:
                tmp_path = Path(tmp_dir) / "pytoolbelt"

                # first thing to do is copy the repo over
                print(f"Copying {PYTOOLBELT_TOOLBELT_ROOT} to {tmp_path}")
                shutil.copytree(src=PYTOOLBELT_TOOLBELT_ROOT, dst=tmp_path)

                # get the git commands pointed at the temp repo
                tmp_git_client = GitClient.from_path(path=tmp_path)

                # check out the tag in the temp repo
                print(f"Checking out tag {tag_reference}")
                tmp_git_client.checkout_tag(tag_reference)

                # create new paths and builder pointed to the temp repo
                tmp_project_paths = ToolbeltPaths(tmp_path)
                tmp_paths = PtVenvPaths(self.paths.meta, tmp_project_paths)
                tmp_ptvenv_config = PtVenvConfig.from_file(tmp_paths.ptvenv_config_file)

                if not self._installation_can_proceed(tmp_ptvenv_config):
                    if not force:
                        return 0

                tmp_builder = PtVenvBuilder(tmp_paths)
                print(f"Building {self.paths.meta.name} version {self.paths.meta.version} from {tag_reference}")
                tmp_builder.build()
                return 0

        else:
            if not self._installation_can_proceed(ptvenv_config):
                if not force:
                    return 0
            self.builder.build()
            return 0

    def _installation_can_proceed(self, current_config: PtVenvConfig) -> bool:
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
                print(
                    f"Python environment {self.paths.meta.name} version {self.paths.meta.version} is already up to date."
                )
                return False
        return True

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
        project = Project()
        return project.release(ptc=ptc, component_paths=self.paths)

    def releases(self, repo: str) -> int:
        repo_config = ToolbeltConfigs.load().get(repo)
        table = PtVenvReleasesTableView(repo_config)
        git_client = GitClient.from_path(self.project_paths.root_path)

        for tag in git_client.ptvenv_releases():
            meta = ComponentMetadata.from_release_tag(tag.name)
            table.add_row(meta.name, meta.version, str(tag.commit.committed_datetime.date()), tag.commit.hexsha)
        table.print_table()
        return 0

    def installed(self) -> int:
        table = PtVenvInstalledTableView()
        installed_ptvenvs = list(self.project_paths.iter_installed_ptvenvs())
        installed_ptvenvs.sort(key=lambda x: (x.version, x.name), reverse=True)
        for installed_ptvenv in installed_ptvenvs:
            ptvenv_paths = PtVenvPaths(installed_ptvenv, self.project_paths)
            table.add_row(installed_ptvenv.name, installed_ptvenv.version, ptvenv_paths.display_install_dir)
        table.print_table()
        return 0

    def fetch(self, repo_config_name: str, keep: bool, build: bool, force: bool) -> None:

        if not keep and not build:
            print("the ptvenv must be either kept with --keep, or built with --build or both, but not none")
            return

        if not build and force:
            print("the --force flag is only valid when building the ptvenv")
            return

        if keep:
            self.raise_if_exists()

        repo_config = self.project_paths.get_pytoolbelt_config().get_repo_config(repo_config_name)

        with tempfile.TemporaryDirectory() as tmpdir:
            print("setting up temp dir...")
            tmpdir_path = Path(tmpdir)

            print("cloning repo...")
            tmp_git_client = GitClient.clone_from_url(repo_config.url, tmpdir_path)

            if isinstance(self.paths.meta.version, str) and self.paths.meta.version == "latest":
                print("latest version being fetched....")

                tags = tmp_git_client.ptvenv_releases(name=self.paths.meta.name, as_names=True)
                latest_meta = ComponentMetadata.get_latest_release(tags)
                latest_release = tmp_git_client.get_tag_reference(latest_meta.release_tag)

            # otherwise we got a version passed in the cli so just assume it exists and check it out and if not... poop.
            else:
                print("passed in version being fetched.")
                try:
                    latest_release = tmp_git_client.get_tag_reference(self.paths.meta.release_tag)
                except IndexError:
                    raise PtVenvCreationError(f"Version {self.paths.meta.version} not found in the repository.")

            tmp_git_client.checkout_tag(latest_release)
            tmp_project_paths = ToolbeltPaths(tmpdir_path)
            tmp_ptvenv_paths = PtVenvPaths(self.paths.meta, tmp_project_paths)

            self.paths.ptvenv_dir.mkdir(parents=True, exist_ok=True)

            # we should only do this when we keep...
            shutil.copytree(tmp_ptvenv_paths.ptvenv_dir, self.paths.ptvenv_dir, dirs_exist_ok=True)

            if build:
                builder = PtVenvBuilder(tmp_ptvenv_paths)
                builder.build()

            # TODO: you need to fix this. gets deleted if already exists.... not good.
            if keep:
                if not self.paths.ptvenv_dir.exists():
                    shutil.rmtree(self.paths.ptvenv_dir)
