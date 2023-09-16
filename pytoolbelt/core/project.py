"""
TODO: Add docstrings to everything
TODO: Check TypeHints and make sure they are as expected
TODO: Add some error handling. We are doing file i/o which could throw exceptions
"""

from pathlib import Path
from typing import Optional, List
from rich.console import Console
from rich.table import Table
from pytoolbelt.environment.config import ProjectTree, CONFIG_FILE_PATH, DEFAULT_PYTHON_VERSION, STANDARD_PYENVS
from pytoolbelt.core.tool import Tool, ToolInfo
from pytoolbelt.core.installer import Installer
from pytoolbelt.core.pyenv import PyEnv
from pytoolbelt.bases import BaseTemplater, BaseCreator
from pytoolbelt.utils import file_handler


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

    @property
    def config_file_path(self) -> Path:
        return CONFIG_FILE_PATH

    @staticmethod
    def get_installer(tool: Tool) -> "Installer":
        return Installer(tool)

    @staticmethod
    def get_tool_info() -> "ToolInfo":
        return ToolInfo()

    @staticmethod
    def new_tool(name: str) -> "Tool":
        return Tool(name)

    def get_project_builder(self) -> "ProjectBuilder":
        return ProjectBuilder(self)

    def get_project_info(self) -> "ProjectInfo":
        return ProjectInfo(self)

    def get_initializer(self) -> "ProjectInitializer":
        return ProjectInitializer(self)

    def get_templater(self) -> "ProjectTemplater":
        return ProjectTemplater(self)


class ProjectInitializer(BaseCreator):

    def __init__(self, project: PyToolBeltProject) -> None:
        super().__init__()
        self.project = project

    @property
    def files(self) -> List[Path]:
        return [self.project.config_file_path]

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


class ProjectTemplater(BaseTemplater):

    def __init__(self, project: PyToolBeltProject) -> None:
        super().__init__()
        self.project = project

    def _template_config_file(self) -> None:
        content = self._render_template("config.yml.template", project=self.project)
        file_handler.write_file(self.project.config_file_path, content)


class ProjectBuilder:

    def __init__(self, project: PyToolBeltProject) -> None:
        self.project = project

    def build(self) -> None:
        self._initialize_project()
        self._template_files()

        for pyenv_name in STANDARD_PYENVS:
            pyenv = self.project.new_pyenv(pyenv_name, DEFAULT_PYTHON_VERSION)
            self._initialize_pyenv(pyenv)
            self._template_pyenv(pyenv)
            self._build_pyenv(pyenv)

    def _initialize_project(self) -> None:
        project_initializer = self.project.get_initializer()
        project_initializer.initialize()

    def _template_files(self) -> None:
        project_templater = self.project.get_templater()
        project_templater.template()

    @staticmethod
    def _initialize_pyenv(pyenv: PyEnv) -> None:
        initializer = pyenv.get_initializer()
        initializer.initialize()

    @staticmethod
    def _template_pyenv(pyenv: PyEnv) -> None:
        templater = pyenv.get_templater()
        templater.template()

    @staticmethod
    def _build_pyenv(pyenv: PyEnv) -> None:
        builder = pyenv.get_builder()
        builder.build()


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
