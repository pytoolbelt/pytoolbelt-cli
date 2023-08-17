from pathlib import Path
from typing import Optional
from pytoolbelt.environment.config import ProjectTree
from pytoolbelt.core.bases import BaseTemplater
from pytoolbelt.core.tool import Tool, ToolInfo
from pytoolbelt.core.pyenv import PyEnv


class PyToolBeltProject:

    def __init__(self, root: Optional[Path] = None) -> None:
        self.root = root or ProjectTree.ROOT_DIRECTORY

    @property
    def environments_path(self) -> Path:
        return ProjectTree.ENVIRONMENTS_DIRECTORY

    @property
    def environment_index_path(self) -> Path:
        return ProjectTree.ENVIRONMENTS_METADATA_DIRECTORY

    @property
    def bin_path(self) -> Path:
        return ProjectTree.BIN_DIRECTORY

    @property
    def tools_path(self) -> Path:
        return ProjectTree.TOOLS_DIRECTORY

    @property
    def config_file_path(self) -> Path:
        return ProjectTree.CONFIG_FILE

    def initialize(self) -> None:
        self.root.mkdir(exist_ok=True)
        self.environments_path.mkdir(exist_ok=True)
        self.environment_index_path.mkdir(exist_ok=True)
        self.bin_path.mkdir(exist_ok=True)
        self.tools_path.mkdir(exist_ok=True)

        if not self.config_file_path.exists():
            self.config_file_path.touch()

        self.new_project_templater().template()

    def new_tool(self, name: str) -> "Tool":
        return Tool(name, self.tools_path)

    @staticmethod
    def new_tool_info() -> "ToolInfo":
        return ToolInfo()

    @staticmethod
    def new_pyenv(name: str, python_version: str) -> "PyEnv":
        return PyEnv(name, python_version)

    def new_project_templater(self) -> "ProjectTemplater":
        return ProjectTemplater(self)

    # TODO: Everything below here is a WIP. It doesn't belong in this file.
    def download_venv_definition(self, name: str, python_version: str) -> None:
        pyenv = self.new_pyenv(name, python_version)
        pyenv_downloader = pyenv.get_downloader()
        pyenv_downloader.download()

    def build_venv(self, name: str, python_version: str) -> None:
        pyenv = self.new_pyenv(name, python_version)
        pyenv_builder = pyenv.get_builder()
        pyenv_builder.build()

    def ensure_venv(self, name) -> None:
        tool = self.new_tool(name)
        tool_metadata = tool.get_metadata()
        tool_metadata_config = tool_metadata.get_metadata_config()
        tool_metadata_config.load(missing_venv_ok=True)

        if not tool_metadata_config.interpreter_path.exists():
            self.download_venv_definition(
                name=tool_metadata_config.interpreter,
                python_version=tool_metadata_config.python_version
            )
            self.build_venv(
                name=tool_metadata_config.interpreter,
                python_version=tool_metadata_config.python_version
            )


class ProjectTemplater(BaseTemplater):

    def __init__(self, project: PyToolBeltProject) -> None:
        super().__init__()
        self.project = project

    def template(self) -> None:
        self._template_config_file()

    def _template_config_file(self) -> None:
        config_template = self.jinja.get_template("config.yml.template")
        content = config_template.render()
        self.project.config_file_path.write_text(content)
