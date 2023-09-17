from typing import List
from pathlib import Path
from pytoolbelt.environment.variables import PYTOOLBELT_CLI_DIRECTORY, PYTOOLBELT_USER_DIRECTORY
from pytoolbelt.bases.initializer import BaseCreator


class PyToolBeltProject:

    @staticmethod
    def get_project_paths() -> "ProjectPaths":
        return ProjectPaths()


class ProjectPaths:

    @property
    def cli_root(self) -> Path:
        return PYTOOLBELT_CLI_DIRECTORY

    @property
    def user_root(self) -> Path:
        return PYTOOLBELT_USER_DIRECTORY

    @property
    def pyenvs(self) -> Path:
        return self.user_root / "pyenvs"

    @property
    def tools(self) -> Path:
        return self.user_root / "tools"

    @property
    def environments(self) -> Path:
        return self.cli_root / "environments"

    @property
    def bin(self) -> Path:
        return self.cli_root / "bin"


class ProjectCreator(BaseCreator):

    def __init__(self, project: PyToolBeltProject) -> None:
        super().__init__()
        self.project = project
        self.paths = self.project.get_project_paths()

    @property
    def files(self) -> List[Path]:
        return []

    @property
    def directories(self) -> List[Path]:
        return [
            self.paths.cli_root,
            self.paths.user_root,
            self.paths.pyenvs,
            self.paths.tools,
            self.paths.environments,
            self.paths.bin
        ]
