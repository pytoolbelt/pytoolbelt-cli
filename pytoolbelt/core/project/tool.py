import requests
import yaml
import zipapp
import zipfile
import shutil
import zipimport
import json
import subprocess
import sys
from rich.console import Console
from rich.table import Table
from pathlib import Path
from typing import Optional, Generator, List
from pytoolbelt.terminal.core.utils import get_jinja_env
from pytoolbelt.terminal.environment.config import ProjectTree, DEFAULT_PYTHON_VERSION
from pytoolbelt.terminal.core.error_handler.exceptions import MetaDataError, InterpreterNotFound, ToolNotFound, \
    ToolExists, ToolDownloadError


class ToolMetaDataConfig:

    def __init__(self, tool_meta: Path) -> None:
        self.tool_meta = tool_meta
        self.data = None
        self.meta = None

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
        return ProjectTree.ENVIRONMENTS_DIRECTORY / self.python_version / self.interpreter / f"venv/bin/python{self.python_version}"

    @property
    def pytest_path(self) -> Path:
        return ProjectTree.ENVIRONMENTS_DIRECTORY / self.python_version / self.interpreter / "venv/bin/pytest"

    def load(self, missing_venv_ok: Optional[bool] = False) -> None:
        with open(self.tool_meta, "r") as f:
            self.data = yaml.safe_load(f)

        self.meta = self.data.get("tool-meta")
        self._validate(missing_venv_ok)

    def _validate(self, missing_venv_ok: bool) -> None:
        if not self.data:
            raise MetaDataError(f"No metadata found for {self.tool_meta}")

        if not self.meta:
            raise MetaDataError(f"No tool-meta found in metadata for {self.tool_meta}")

        if not self.python_version:
            raise MetaDataError(f"No python version found in metadata for {self.tool_meta}")

        if not self.interpreter and not self.requirements and not self.tool_meta.name.startswith("base"):
            raise MetaDataError(f"No interpreter or requirements found in metadata for {self.tool_meta}")

        if self.interpreter and self.requirements:
            raise MetaDataError(f"Cannot have both interpreter and requirements in metadata for {self.tool_meta}")

        if not missing_venv_ok:
            if self.interpreter and not self.interpreter_path.exists():
                raise InterpreterNotFound(f"Interpreter {self.interpreter_path} not found")


class Tool:
    def __init__(self, name: str, tools_path: Path) -> None:
        self.name = name
        self.tools_path = tools_path

    @property
    def tool_root(self) -> Path:
        return self.tools_path / self.name

    @property
    def src_directory(self) -> Path:
        return self.tool_root / "src"

    @property
    def tool_meta(self) -> Path:
        return self.tool_root / f"meta.yml"

    def purge(self) -> None:
        shutil.rmtree(self.tool_root)

    def get_metadata(self) -> "ToolMetaData":
        return ToolMetaData(self)

    def get_builder(self) -> "ToolBuilder":
        return ToolBuilder(self)

    def get_templater(self) -> "ToolTemplater":
        return ToolTemplater(self)

    def get_packager(self) -> "ToolPackager":
        return ToolPackager(self)

    def get_uploader(self) -> "ToolUploader":
        return ToolUploader(self)

    def get_downloader(self) -> "ToolDownloader":
        return ToolDownloader(self)

    def get_publisher(self) -> "ToolPublisher":
        return ToolPublisher(self)

    def get_formatter(self) -> "ToolFormatter":
        return ToolFormatter(self)

    def get_test_runner(self) -> "ToolTestRunner":
        return ToolTestRunner(self)


class ToolMetaData:
    def __init__(self, tool: Tool) -> None:
        self.tool = tool

    @property
    def test_path(self) -> Path:
        return self.tool.tool_root / "tests"

    @property
    def test_init_file(self) -> Path:
        return self.test_path / "__init__.py"

    @property
    def test_cli_file(self) -> Path:
        return self.test_path / "test_cli.py"

    @property
    def tool_cli_file(self) -> Path:
        return self.tool.src_directory / f"cli.py"

    @property
    def tool_info_file(self) -> Path:
        return self.tool.src_directory / f"info.py"

    @property
    def entrypoint_file(self) -> Path:
        return self.tool.src_directory / f"__main__.py"

    def exists(self) -> None:
        if not self.tool.tool_root.exists():
            raise ToolNotFound(f"Tool {self.tool.name} not found")

    def save(self) -> None:
        if self.tool.tool_root.exists():
            raise ToolExists(f"Tool {self.tool.name} already exists")

        self.tool.tool_root.mkdir(exist_ok=True)
        self.tool.src_directory.mkdir(exist_ok=True)

        self.tool.tool_meta.touch(exist_ok=True)

        self.entrypoint_file.touch(exist_ok=True)

        self.test_path.mkdir(exist_ok=True)
        self.test_init_file.touch(exist_ok=True)
        self.test_cli_file.touch(exist_ok=True)
        self.tool_info_file.touch(exist_ok=True)

    def get_metadata_config(self) -> ToolMetaDataConfig:
        return ToolMetaDataConfig(self.tool.tool_meta)


class ToolBuilder:
    def __init__(self, tool: Tool) -> None:
        self.tool = tool

    @property
    def executable_path(self) -> Path:
        return ProjectTree.BIN_DIRECTORY / self.tool.name

    @property
    def tool_root_executable_path(self) -> Path:
        return self.tool.tool_root / self.tool.name

    def build(self, install: Optional[bool] = False) -> None:
        metadata_config = self.tool.get_metadata().get_metadata_config()
        metadata_config.load()

        if self.tool_root_executable_path.exists():
            self.tool_root_executable_path.unlink()

        target = self.executable_path if install else self.tool_root_executable_path

        zipapp.create_archive(
            source=self.tool.src_directory,
            target=target,
            interpreter=metadata_config.interpreter_path.as_posix(),
        )


class ToolTemplater:

    def __init__(self, tool: Tool) -> None:
        self.tool = tool
        self.jinja = get_jinja_env()

    def template(self) -> None:
        self._template_entrypoint_file()
        self._template_test_cli_file()
        self._template_info_file()
        self._template_meta_file()

    def _template_cli_file(self) -> None:

        # TODO: Review if this method is really needed. Perhaps we don't need a file called cli.py at all????
        template = self.jinja.get_template("cli.py.template")
        content = template.render(tool_name=self.tool.name)
        self.tool.get_metadata().tool_cli_file.write_text(content)

    def _template_entrypoint_file(self) -> None:
        template = self.jinja.get_template("__main__.py.template")
        content = template.render(tool_name=self.tool.name)
        self.tool.get_metadata().entrypoint_file.write_text(content)

    def _template_test_cli_file(self) -> None:
        template = self.jinja.get_template("test_cli.py.template")
        content = template.render(tool_name=self.tool.name)
        self.tool.get_metadata().test_cli_file.write_text(content)

    def _template_info_file(self) -> None:
        template = self.jinja.get_template("info.py.template")
        content = template.render(tool_name=self.tool.name)
        self.tool.get_metadata().tool_info_file.write_text(content)

    def _template_meta_file(self) -> None:
        template = self.jinja.get_template("meta.yml.template")
        content = template.render(tool_name=self.tool.name, python_version=DEFAULT_PYTHON_VERSION)
        self.tool.tool_meta.write_text(content)


class ToolPackager:

    def __init__(self, tool: Tool) -> None:
        self.tool = tool

    @property
    def zipfile(self) -> Path:
        return self.tool.tool_root / f"{self.tool.name}.zip"

    @property
    def zipfile_temp(self) -> Path:
        return ProjectTree.TEMP_DIRECTORY / f"{self.tool.name}.zip"

    def purge(self) -> None:
        if self.zipfile.exists():
            self.zipfile.unlink()

        if self.zipfile_temp.exists():
            self.zipfile_temp.unlink()

    def tool_files(self) -> Generator[Path, None, None]:
        for file in self.tool.tool_root.glob("**/*"):
            if file.is_file() and not file.suffix == ".zip":
                yield file

    def package(self) -> None:
        with zipfile.ZipFile(self.zipfile, mode="w") as zip_file:
            for file in self.tool_files():
                content = file.read_bytes()  # Using read_bytes for both text and binary files
                relative_path = file.relative_to(self.tool.tool_root)
                zip_file.writestr(str(relative_path), content)

    def unpack(self) -> None:
        with zipfile.ZipFile(self.zipfile_temp, mode="r") as zip_file:
            zip_file.extractall(self.tool.tool_root)


class ToolUploader:

    def __init__(self, tool: Tool) -> None:
        self.tool = tool

    def upload(self) -> str:
        tool_packager = self.tool.get_packager()

        url = f"http://localhost:8000/upload/"

        files = {
            "uploaded_file": (tool_packager.zipfile.name, open(tool_packager.zipfile, "rb"))
        }

        response = requests.post(url, files=files)
        return response.json()


class ToolDownloader:

    def __init__(self, tool: Tool) -> None:
        self.tool = tool

    def download(self) -> None:
        url = f"http://localhost:8000/tools/{self.tool.name}"
        response = requests.get(url)

        if response.status_code != 200:
            raise ToolDownloadError(f"Failed to download tool {self.tool.name}")

        tool_packager = self.tool.get_packager()

        with open(tool_packager.zipfile_temp, "wb") as file:
            file.write(response.content)


class ToolPublisher:

    def __init__(self, tool: Tool) -> None:
        self.tool = tool

    def publish(self) -> None:
        tool_packager = self.tool.get_packager()
        tool_packager.package()

        tool_uploader = self.tool.get_uploader()
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

    def check(self) -> None:
        self.black_check()
        self.isort_check()

    def format(self) -> None:
        self.isort_format()
        self.black_format()

    def black_check(self) -> None:
        subprocess.run(
            [
                "black",
                "--line-length",
                self.line_length,
                "--skip-string-normalization",
                "--check",
                self.tool.tool_root.as_posix(),
            ],
            check=True,
        )

    def black_format(self) -> None:
        subprocess.run(
            [
                "black",
                "--line-length",
                self.line_length,
                "--skip-string-normalization",
                self.tool.tool_root.as_posix(),
            ],
            check=True,
        )

    def isort_check(self) -> None:
        subprocess.run(
            [
                "isort",
                "--profile","black",
                "--check",
                self.tool.tool_root.as_posix(),
            ],
            check=True,
        )

    def isort_format(self) -> None:
        subprocess.run(
            [
                "isort",
                "--profile","black",
                self.tool.tool_root.as_posix(),
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
