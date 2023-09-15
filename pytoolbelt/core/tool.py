import requests
import yaml
import zipfile
import zipimport
import json
import subprocess
import sys
from rich.console import Console
from rich.table import Table
from pathlib import Path
from typing import Generator, List
from pytoolbelt.utils import file_handler
from pytoolbelt.bases import BaseTemplater, BaseRemoteManager
from pytoolbelt.environment.config import ProjectTree, DEFAULT_PYTHON_VERSION
from pytoolbelt.core.exceptions import MetaDataError, InterpreterNotFound, ToolExists, ToolDownloadError


class Tool:

    def __init__(self, name: str) -> None:
        self.name = name

    def get_metadata(self) -> "ToolMetaData":
        return ToolMetaData(self)

    def get_templater(self) -> "ToolTemplater":
        return ToolTemplater(self)

    def get_packager(self) -> "ToolPackager":
        return ToolPackager(self)

    def get_remote_manager(self) -> "ToolRemoteManager":
        return ToolRemoteManager(self)

    def get_initializer(self) -> "ToolInitializer":
        metadata = self.get_metadata()
        return ToolInitializer(metadata)

    def get_publisher(self) -> "ToolPublisher":
        return ToolPublisher(self)

    def get_formatter(self) -> "ToolFormatter":
        return ToolFormatter(self)

    def get_test_runner(self) -> "ToolTestRunner":
        return ToolTestRunner(self)


class ToolMetaData:

    def __init__(self, tool: Tool) -> None:

        self.tool = tool
        self.data = None
        self.meta = None

    @property
    def tool_root(self) -> Path:
        return ProjectTree.TOOLS_DIRECTORY / self.tool.name

    @property
    def src_directory(self) -> Path:
        return self.tool_root / "src"

    @property
    def executable_path(self) -> Path:
        return ProjectTree.BIN_DIRECTORY / self.tool.name

    @property
    def test_path(self) -> Path:
        return self.tool_root / "tests"

    @property
    def test_init_file(self) -> Path:
        return self.test_path / "__init__.py"

    @property
    def tool_metadata_file(self) -> Path:
        return self.tool_root / f"meta.yml"

    @property
    def tool_info_file(self) -> Path:
        return self.src_directory / f"info.py"

    @property
    def entrypoint_file(self) -> Path:
        return self.src_directory / f"__main__.py"

    @property
    def python_version(self) -> str:
        return self.meta.get("python_version", DEFAULT_PYTHON_VERSION)

    @property
    def requirements(self) -> list[str]:
        return self.meta.get("requirements", [])

    @property
    def interpreter(self) -> str:
        return self.meta.get("interpreter", "")

    @property
    def interpreter_path(self) -> Path:
        return ProjectTree.ENVIRONMENTS_DIRECTORY / self.python_version / self.interpreter / "venv" / "bin" / f"python{self.python_version}"

    def raise_if_exists(self) -> None:
        if file_handler.check_exists(self.tool_root):
            raise ToolExists(f"Tool {self.tool.name} already exists. Please choose a different name, or remove the existing tool.")

    def load(self) -> None:
        self.data = file_handler.read_file(self.tool_metadata_file)
        self.meta = yaml.safe_load(self.data)["tool-meta"]
        self._validate()

    def _raise_if_no_data(self) -> None:
        if not self.data:
            raise MetaDataError(f"No metadata found for tool {self.tool.name}")

    def _raise_if_no_meta(self) -> None:
        if not self.meta:
            raise MetaDataError(f"No tool-meta found in metadata for tool {self.tool.name}")

    def _raise_if_no_python_version(self) -> None:
        if not self.python_version:
            raise MetaDataError(f"No python version found in metadata for tool {self.tool.name}")

    def _raise_if_no_interpreter(self) -> None:
        if not self.interpreter:
            raise MetaDataError(f"No interpreter found in metadata for tool {self.tool.name}")

    def _raise_if_interpreter_not_found(self) -> None:
        if not file_handler.check_exists(self.interpreter_path):
            raise InterpreterNotFound(f"Interpreter {self.interpreter_path} not found")

    def _validate(self) -> None:
        self._raise_if_no_data()
        self._raise_if_no_meta()
        self._raise_if_no_python_version()
        self._raise_if_no_interpreter()
        self._raise_if_interpreter_not_found()


class ToolInitializer:

    def __init__(self, tool_metadata: ToolMetaData) -> None:
        self.tool_metadata = tool_metadata

    def initialize(self) -> None:
        self._create_directories()
        self._create_files()

    @property
    def paths(self) -> List[Path]:
        return [
            self.tool_metadata.tool_root,
            self.tool_metadata.src_directory,
            self.tool_metadata.test_path,
        ]

    @property
    def files(self) -> List[Path]:
        return [
            self.tool_metadata.entrypoint_file,
            self.tool_metadata.test_init_file,
            self.tool_metadata.tool_info_file,
        ]

    def _create_directories(self) -> None:
        for path in self.paths:
            file_handler.create_directory(path, parents=True)

    def _create_files(self) -> None:
        for file in self.files:
            file_handler.create_file_if_not_exists(file)


class ToolTemplater(BaseTemplater):

    def __init__(self, tool: Tool) -> None:
        super().__init__()
        self.tool = tool
        self.tool_metadata = self.tool.get_metadata()

    def _template_entrypoint_file(self) -> None:
        template = self.jinja.get_template("__main__.py.template")
        content = template.render(tool_name=self.tool.name)
        file_handler.write_file(self.tool_metadata.entrypoint_file, content)

    def _template_info_file(self) -> None:
        template = self.jinja.get_template("info.py.template")
        content = template.render(tool_name=self.tool.name)
        file_handler.write_file(self.tool_metadata.tool_info_file, content)

    def _template_meta_file(self) -> None:
        template = self.jinja.get_template("meta.yml.template")
        content = template.render(tool_name=self.tool.name, python_version=DEFAULT_PYTHON_VERSION)
        file_handler.write_file(self.tool_metadata.tool_metadata_file, content)


class ToolPackager:

    def __init__(self, tool: Tool) -> None:
        self.tool = tool
        self.tool_metadata = self.tool.get_metadata()

    @property
    def zipfile(self) -> Path:
        return self.tool_metadata.tool_root / f"{self.tool.name}.zip"

    @property
    def zipfile_temp(self) -> Path:
        return ProjectTree.TEMP_DIRECTORY / f"{self.tool.name}.zip"

    def purge(self) -> None:
        file_handler.delete_file_if_exists(self.zipfile)
        file_handler.delete_file_if_exists(self.zipfile_temp)

    def tool_files(self) -> Generator[Path, None, None]:
        for file in self.tool_metadata.tool_root.glob("**/*"):
            if file.is_file() and not file.suffix == ".zip":
                yield file

    def package(self) -> None:
        with zipfile.ZipFile(self.zipfile, mode="w") as zip_file:
            for file in self.tool_files():
                content = file.read_bytes()
                relative_path = file.relative_to(self.tool_metadata.tool_root)
                zip_file.writestr(str(relative_path), content)

    def unpack(self) -> None:
        with zipfile.ZipFile(self.zipfile_temp, mode="r") as zip_file:
            zip_file.extractall(self.tool_metadata.tool_root)


class ToolRemoteManager(BaseRemoteManager):

    def __init__(self, tool: Tool) -> None:
        super().__init__()
        self.tool = tool

    @property
    def upload_url(self) -> str:
        return f"http://localhost:8000/upload/"

    @property
    def download_url(self) -> str:
        return f"http://localhost:8000/tools/{self.tool.name}"

    def upload(self) -> None:
        pass

    def download(self) -> None:
        pass


class ToolPublisher:

    def __init__(self, tool: Tool) -> None:
        self.tool = tool

    def publish(self) -> None:
        tool_packager = self.tool.get_packager()
        tool_packager.package()

        tool_uploader = self.tool.get_remote_manager()
        tool_uploader.upload()

        tool_packager.purge()


class ToolInfo:

    @property
    def bin_directory(self) -> Path:
        return ProjectTree.BIN_DIRECTORY

    def installed_tools(self) -> List[Path]:
        return [tool for tool in self.bin_directory.iterdir() if tool.is_file()]

    def display(self) -> None:
        console = Console()
        table = Table()

        table.add_column("Tool Name")
        table.add_column("Description")
        table.add_column("Author")
        table.add_column("Version")
        table.add_column("Site")

        for tool in self.installed_tools():
            try:
                zipimporter = zipimport.zipimporter(tool.as_posix())
                info = zipimporter.load_module("info")
                data = json.loads(info.info())
                table.add_row(
                    data["name"],
                    data["description"],
                    data["author"],
                    data["version"],
                    data["site"],
                )
            except zipimport.ZipImportError:
                table.add_row(tool.name, "", "", "", "")

        console.print(table)


class ToolFormatter:
    def __init__(self, tool: Tool) -> None:
        self.line_length = "120"
        self.tool = tool
        self.metadata = self.tool.get_metadata()

    def check(self) -> None:
        self.black_check()
        self.isort_check()

    def format(self) -> None:
        self.isort_format()
        self.black_format()

    @property
    def black_path(self) -> Path:
        return ProjectTree.ENVIRONMENTS_DIRECTORY / DEFAULT_PYTHON_VERSION / "qa" / "venv/bin/black"

    @property
    def isort_path(self) -> Path:
        return ProjectTree.ENVIRONMENTS_DIRECTORY / DEFAULT_PYTHON_VERSION / "qa" / "venv/bin/isort"

    def black_check(self) -> None:

        subprocess.run(
            [
                self.black_path.as_posix(),
                "--line-length",
                self.line_length,
                "--skip-string-normalization",
                "--check",
                self.metadata.tool_root.as_posix(),
            ],
            check=True,
        )

    def black_format(self) -> None:
        subprocess.run(
            [
                self.black_path.as_posix(),
                "--line-length",
                self.line_length,
                "--skip-string-normalization",
                self.metadata.tool_root.as_posix(),
            ],
            check=True,
        )

    def isort_check(self) -> None:
        subprocess.run(
            [
                self.isort_path.as_posix(),
                "--profile","black",
                "--check",
                self.metadata.tool_root.as_posix(),
            ],
            check=True,
        )

    def isort_format(self) -> None:
        subprocess.run(
            [
                self.isort_path.as_posix(),
                "--profile", "black",
                self.metadata.tool_root.as_posix(),
            ],
            check=True,
        )


class ToolTestRunner:

    def __init__(self, tool: Tool) -> None:
        self.tool = tool

    def run(self) -> None:

        tool_metadata_config = self.tool.get_metadata().get_metadata_config()
        tool_metadata_config.load()

        sys.path.append(self.tool.tool_root.as_posix())

        subprocess.run([
            tool_metadata_config.pytest_path,
            self.tool.get_metadata().test_path
        ])
