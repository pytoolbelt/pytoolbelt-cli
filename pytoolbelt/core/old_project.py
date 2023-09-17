from pathlib import Path
from typing import Optional, List
from rich.console import Console
from rich.table import Table
from pytoolbelt.environment.config import ProjectTree
from pytoolbelt.core.tool import Tool, ToolInfo
from pytoolbelt.core.installer import Installer
from pytoolbelt.bases import BaseCreator


class PyToolBeltProject:

    def __init__(self, root: Optional[Path] = None) -> None:
        self.cli_root = root or ProjectTree.CLI_ROOT_DIRECTORY
        self.user_root = ProjectTree.USER_ROOT_DIRECTORY

    def project_exists(self) -> bool:
        return self.cli_root.exists() and self.user_root.raise_if_exists()

    @property
    def environments_path(self) -> Path:
        return ProjectTree.ENVIRONMENTS_DIRECTORY

    @property
    def pyenvs_path(self) -> Path:
        return ProjectTree.PYENVS_DIRECTORY

    @property
    def bin_path(self) -> Path:
        return ProjectTree.BIN_DIRECTORY

    @property
    def tools_path(self) -> Path:
        return ProjectTree.TOOLS_DIRECTORY

    @property
    def temp_path(self) -> Path:
        return ProjectTree.TEMP_DIRECTORY

    @staticmethod
    def get_installer(tool: Tool) -> "Installer":
        return Installer(tool)

    @staticmethod
    def get_tool_info() -> "ToolInfo":
        return ToolInfo()

    @staticmethod
    def new_tool(name: str) -> "Tool":
        return Tool(name)

    def get_project_info(self) -> "ProjectInfo":
        return ProjectInfo(self)

    def get_initializer(self) -> "ProjectCreator":
        return ProjectCreator(self)


class ProjectCreator(BaseCreator):

    def __init__(self, project: PyToolBeltProject) -> None:
        super().__init__()
        self.project = project

    @property
    def files(self) -> List[Path]:
        return []

    @property
    def directories(self) -> List[Path]:
        return [
            self.project.cli_root,
            self.project.user_root,
            self.project.environments_path,
            self.project.pyenvs_path,
            self.project.bin_path,
            self.project.tools_path,
            self.project.temp_path
        ]


class ProjectInfo:

    def __init__(self, project: PyToolBeltProject) -> None:
        self.project = project

    def display(self) -> None:
        console = Console()
        table = Table()

        table.add_column("Name")
        table.add_column("Path")
        table.add_column("Description")

        table.add_row("PyToolBelt Root", self.project.cli_root.as_posix(), "Root directory for the pytoolbelt cli")
        table.add_row("Bin", self.project.bin_path.as_posix(), "Directory for installed tools")
        table.add_row("Environments", self.project.environments_path.as_posix(), "Directory for virtual environments")
        table.add_row("Project Root", self.project.user_root.as_posix(), "Root directory for the pytoolbelt project")
        table.add_row("Tools", self.project.tools_path.as_posix(), "Directory for tool source code")
        table.add_row("PyEnvs", self.project.pyenvs_path.as_posix(), "Directory for venv definitions")
        table.add_row("Temp", self.project.temp_path.as_posix(), "Directory for temporary files")
        console.print(table)
