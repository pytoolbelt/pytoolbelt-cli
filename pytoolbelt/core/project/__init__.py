from typing import Optional
from pathlib import Path
from .project_components import ProjectPaths, ProjectTemplater
from .ptvenv_components import PtVenvPaths, PtVenvTemplater, PtVenvBuilder
from pytoolbelt.core.git_commands import GitCommands
from pytoolbelt.core.data_classes.component_metadata import ComponentMetadata


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
    def from_cli(cls, string: str, root_path: Optional[Path] = None) -> "PtVenv":
        meta = ComponentMetadata.as_ptvenv(string)
        return cls(meta, root_path)

    @classmethod
    def from_release_tag(cls, tag: str, root_path: Optional[Path] = None) -> "PtVenv":
        meta = ComponentMetadata.from_release_tag(tag)
        return cls(meta, root_path)

    @property
    def release_tag(self) -> str:
        return self.paths.meta.release_tag

    def create(self) -> None:
        self.paths.create()
        self.templater.template_new_venvdef_file()
