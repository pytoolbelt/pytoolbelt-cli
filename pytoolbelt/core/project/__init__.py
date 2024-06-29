from typing import Optional
from pathlib import Path
import shutil
from .project_components import ProjectPaths, ProjectTemplater
from .ptvenv_components import PtVenvPaths, PtVenvTemplater, PtVenvBuilder, PtVenvConfig
from pytoolbelt.core.git_commands import GitCommands
from pytoolbelt.core.data_classes.component_metadata import ComponentMetadata
from semver import Version
from pytoolbelt.core.exceptions import PtVenvCreationError, PtVenvNotFoundError
from pytoolbelt.core.tools import hash_config


class Project:

    def __init__(self, root_path: Optional[Path] = None, **kwargs) -> None:
        self.paths = kwargs.get("paths", ProjectPaths(project_root=root_path))
        self.templater = kwargs.get("templater", ProjectTemplater(self.paths))

    def create(self, overwrite: Optional[bool] = False) -> None:
        self.paths.create()
        self.templater.template_new_project_files(overwrite)
        GitCommands.init_if_not_exists(self.paths.project_dir)


class PtVenv:

    def __init__(self, meta: ComponentMetadata, root_path: Optional[Path] = None, **kwargs) -> None:
        self.project_paths = kwargs.get("project_paths", ProjectPaths(root_path))
        self.paths = kwargs.get("paths", PtVenvPaths(meta, self.project_paths))
        self.templater = kwargs.get("templater", PtVenvTemplater(self.paths))
        self.builder = kwargs.get("builder", PtVenvBuilder(self.paths))

    @classmethod
    def from_cli(cls, string: str, root_path: Optional[Path] = None, creation: Optional[bool] = False, deletion: Optional[bool] = False, build: Optional[bool] = False) -> "PtVenv":
        meta = ComponentMetadata.as_ptvenv(string)
        inst = cls(meta, root_path)

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
            config = PtVenvConfig.from_file(inst.paths.ptvenv_config_file)
            inst.paths.meta.version = Version.parse(config.version)
            return inst

        return inst

    @classmethod
    def from_release_tag(cls, tag: str, root_path: Optional[Path] = None) -> "PtVenv":
        meta = ComponentMetadata.from_release_tag(tag)
        return cls(meta, root_path)

    @property
    def release_tag(self) -> str:
        return self.paths.meta.release_tag

    def raise_if_exists(self) -> None:
        if self.paths.ptvenv_dir.exists():
            raise PtVenvCreationError(f"Python environment {self.paths.meta.name} already exists.")

    def create(self) -> None:
        self.raise_if_exists()
        self.paths.create()
        self.templater.template_new_venvdef_file()

    def build(self, force: Optional[bool] = False) -> None:

        # force is set so just build and exit, regardless of the state of the environment
        if force:
            self.builder.build()
            return

        # if the installation directory doesn't exist, this is the first time we're building so just build.
        if not self.paths.install_dir.exists():
            self.builder.build()
            return

        # the installation directory exists, so we need to check if the configuration has changed
        # if it has, we need to warn the user that the environment definition has changed, however
        # the version has not been updated. This could lead to unexpected behavior.
        if self.paths.install_dir.exists():

            current_config = PtVenvConfig.from_file(self.paths.ptvenv_config_file)
            installed_config = PtVenvConfig.from_file(self.paths.installed_config_file)

            hashed_current_config = hash_config(current_config)
            hashed_installed_config = hash_config(installed_config)

            installed_hash = self.paths.installed_hash_file.read_text()

            if installed_hash != hashed_installed_config:
                raise PtVenvCreationError(f"ptvenv definition for {self.paths.meta.name} version {self.paths.meta.version} has been modified since install. "
                                          f"Please run 'ptvenv build --force' to rebuild the environment. This will replace {self.paths.meta.name} version {self.paths.meta.version} with the new version definition.")

            if hashed_current_config != hashed_installed_config:
                if current_config.version != installed_config.version:
                    self.builder.build()
                    return

                raise PtVenvCreationError(f"ptvenv definition for {self.paths.meta.name} version {self.paths.meta.version} has been modified since install. "
                                          f"Please run 'ptvenv build --force' to rebuild the environment. This will replace {self.paths.meta.name} version {self.paths.meta.version} with the new version definition.")

            print(f"Python environment {self.paths.meta.name} version {self.paths.meta.version} is already up to date.")

    def delete(self, _all: bool) -> None:
        if self.paths.install_dir.exists():
            if _all:
                shutil.rmtree(self.paths.install_root_dir)
            else:
                shutil.rmtree(self.paths.install_dir.parent)
        else:
            raise PtVenvNotFoundError(f"Python environment {self.paths.meta.name} version {self.paths.meta.version} is not installed.")

    def bump(self, part: str) -> None:
        config = PtVenvConfig.from_file(self.paths.ptvenv_config_file)
        next_version = self.paths.meta.version.next_version(part)
        config.version = str(next_version)
        self.paths.write_to_config_file(config)
