from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.table import Table
from pytoolbelt.environment.config import ProjectTree, CONFIG_FILE_PATH, DEFAULT_PYTHON_VERSION
from pytoolbelt.core.bases import BaseTemplater
from pytoolbelt.core.tool import Tool, ToolInfo
from pytoolbelt.core.installer import Installer
from pytoolbelt.core.pyenv import PyEnv


class PyToolBeltProject:

    def __init__(self, root: Optional[Path] = None) -> None:
        self.cli_root = root or ProjectTree.CLI_ROOT_DIRECTORY
        self.user_root = ProjectTree.USER_ROOT_DIRECTORY

    def project_exists(self) -> bool:
        return self.cli_root.exists() and self.user_root.exists()

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
    def new_pyenv(name: str, python_version: str) -> "PyEnv":
        return PyEnv(name, python_version)

    def get_project_info(self) -> "ProjectInfo":
        return ProjectInfo(self)

    def new_tool(self, name: str) -> "Tool":
        return Tool(name, self.tools_path)

    def get_initializer(self) -> "ProjectInitializer":
        return ProjectInitializer(self)

    def get_project_templater(self) -> "ProjectTemplater":
        return ProjectTemplater(self)


class ProjectInitializer:

    def __init__(self, project: PyToolBeltProject) -> None:
        self.project = project

    def initialize(self) -> None:
        self.project.cli_root.mkdir(exist_ok=True)
        self.project.user_root.mkdir(exist_ok=True)
        self.project.environments_path.mkdir(exist_ok=True)
        self.project.pyenvs_path.mkdir(exist_ok=True)
        self.project.bin_path.mkdir(exist_ok=True)
        self.project.tools_path.mkdir(exist_ok=True)

        if not self.project.config_file_path.exists():
            self.project.config_file_path.touch()

        self.project.get_project_templater().template()

        for name in "base", "qa":
            pyenv = self.project.new_pyenv(name, DEFAULT_PYTHON_VERSION)
            pyenv_builder = pyenv.get_builder()
            pyenv_builder.build()


class ProjectTemplater(BaseTemplater):

    def __init__(self, project: PyToolBeltProject) -> None:
        super().__init__()
        self.project = project

    def template(self) -> None:
        self._template_config_file()
        self._template_standard_pyenvs()

    def _template_config_file(self) -> None:
        config_template = self.jinja.get_template("config.yml.template")
        content = config_template.render()
        self.project.config_file_path.write_text(content)

    def _template_standard_pyenvs(self) -> None:
        for name in "base", "qa":
            pyenv = self.project.new_pyenv(name, DEFAULT_PYTHON_VERSION)
            pyenv_templater = pyenv.get_templater()
            pyenv_templater.template(name)


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
