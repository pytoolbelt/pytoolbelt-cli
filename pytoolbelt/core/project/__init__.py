from typing import Optional
from pathlib import Path
import shutil
from .project_components import ProjectPaths, ProjectTemplater
from .ptvenv_components import PtVenvPaths, PtVenvTemplater, PtVenvBuilder, PtVenvConfig
from pytoolbelt.core.git_commands import GitCommands
from pytoolbelt.core.data_classes.component_metadata import ComponentMetadata
from semver import Version
from pytoolbelt.core.exceptions import PtVenvCreationError, PtVenvNotFoundError


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
    def from_cli(cls, string: str, root_path: Optional[Path] = None, creation: Optional[bool] = False) -> "PtVenv":
        meta = ComponentMetadata.as_ptvenv(string)
        inst = cls(meta, root_path)

        if creation:
            inst.paths.meta.version = Version.parse("0.0.1")
            return inst

        if isinstance(inst.paths.meta.version, str):
            if inst.paths.meta.version == "latest":
                latest_installed_version = inst.paths.get_latest_installed_version()
                inst.paths.meta.version = latest_installed_version
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

    def build(self) -> None:
        self.builder.load_config()
        self.builder.build()

    def delete(self, _all: bool) -> None:
        if self.paths.install_dir.exists():
            if _all:
                shutil.rmtree(self.paths.install_root_dir)
            else:
                shutil.rmtree(self.paths.install_dir.parent)
        else:
            raise PtVenvNotFoundError(f"Python environment {self.paths.meta.name} version {self.paths.meta.version} is not installed.")
