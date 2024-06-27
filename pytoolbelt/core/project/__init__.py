from .project_components import ProjectPaths, ProjectTemplater
from pytoolbelt.core.git_commands import GitCommands
from typing import Optional
from pathlib import Path


class Project:

    def __init__(self, root_path: Optional[Path] = None, **kwargs) -> None:
        self.paths = kwargs.get("paths", ProjectPaths(project_root=root_path))
        self.templater = kwargs.get("templater", ProjectTemplater(self.paths))

    def create(self, overwrite: Optional[bool] = False) -> None:
        self.paths.create()
        self.templater.template_new_project_files(overwrite)
        GitCommands.init_if_not_exists(self.paths.project_dir)
