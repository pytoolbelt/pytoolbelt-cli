import zipfile
from pytoolbelt.model_utils.tool import ToolMetaDataModelFactory
from pytoolbelt.core.project import ProjectPaths
from pytoolbelt.bases.creator import BaseCreator
from pytoolbelt.core.exceptions import ToolExistsError
from pytoolbelt.utils.file_handler import FileHandler
from pathlib import Path
from typing import List, Iterator


class Tool:

    def __init__(self, name: str) -> None:
        self._name = name
        self._project_paths = ProjectPaths()

    @property
    def name(self) -> str:
        return self._name

    @property
    def project_paths(self) -> ProjectPaths:
        return self._project_paths

    def get_paths(self) -> "ToolPaths":
        return ToolPaths(self)

    def get_creator(self) -> "ToolCreator":
        return ToolCreator(self)

    def get_writer(self) -> "ToolWriter":
        return ToolWriter(self)

    def get_destroyer(self) -> "ToolDestroyer":
        return ToolDestroyer(self)

    def get_zipper(self) -> "ToolZipper":
        return ToolZipper(self)

    def get_cleaner(self) -> "ToolCleaner":
        return ToolCleaner(self)


class ToolPaths:

    def __init__(self, tool: Tool) -> None:
        self.tool = tool

    @property
    def tool_root_directory(self) -> Path:
        return self.tool.project_paths.tools / self.tool.name

    @property
    def src_directory(self) -> Path:
        return self.tool_root_directory / "src"

    @property
    def executable_file(self) -> Path:
        return self.tool.project_paths.bin / self.tool.name

    @property
    def tests_directory(self) -> Path:
        return self.tool_root_directory / "tests"

    @property
    def tests_init_file(self) -> Path:
        return self.tests_directory / "__init__.py"

    @property
    def tool_metadata_file(self) -> Path:
        return self.tool_root_directory / "metadata.yml"

    @property
    def entrypoint_file(self) -> Path:
        return self.src_directory / f"__main__.py"

    @property
    def zipfile(self) -> Path:
        return self.tool.project_paths.zip_archives / self.tool.name / f"{self.tool.name}.zip"

    @property
    def temp_zipfile(self) -> Path:
        return self.tool.project_paths.temp / f"{self.tool.name}.zip"

    def iter_tool_files(self) -> Iterator[Path]:
        for file in self.tool_root_directory.glob("**/*"):
            if file.is_file() and not file.suffix == ".zip":
                yield file


class ToolCreator(BaseCreator):

    def __init__(self, tool: Tool) -> None:
        self.tool = tool
        self.paths = self.tool.get_paths()

    @property
    def directories(self) -> List[Path]:
        return [
            self.paths.tool_root_directory,
            self.paths.src_directory,
            self.paths.tests_directory
        ]

    @property
    def files(self) -> List[Path]:
        return [
            self.paths.entrypoint_file,
            self.paths.tool_metadata_file,
            self.paths.tests_init_file
        ]

    def _exists(self) -> None:
        if self.paths.tool_root_directory.exists():
            raise ToolExistsError(f"{self.tool.name} already exists.")


class ToolWriter:

    def __init__(self, tool: Tool) -> None:
        self.tool = tool

    def write(self) -> None:
        tool_model = ToolMetaDataModelFactory.new(self.tool.name)
        paths = self.tool.get_paths()

        file_handler = FileHandler(paths.tool_metadata_file)
        file_handler.write_yml_file(content=tool_model.model_dump())


class ToolDestroyer:

    def __init__(self, tool: Tool) -> None:
        self.tool = tool

    def destroy(self) -> None:
        paths = self.tool.get_paths()

        file_handler = FileHandler(paths.tool_root_directory)
        file_handler.delete_directory()

        file_handler.path = paths.executable_file
        file_handler.delete_file_if_exists()


class ToolZipper:

    def __init__(self, tool: Tool) -> None:
        self.tool = tool
        self.paths = self.tool.get_paths()

    def _create_zip_archive_directory(self) -> None:
        file_handler = FileHandler(self.paths.zipfile.parent)
        file_handler.create_directory(parents=True)

    def zip(self) -> None:
        self._create_zip_archive_directory()
        with zipfile.ZipFile(self.paths.zipfile, "w") as zip_file:
            for file in self.paths.iter_tool_files():
                zip_file.write(file, arcname=file.relative_to(self.paths.tool_root_directory))

    def unzip(self) -> None:
        with zipfile.ZipFile(self.paths.temp_zipfile, "r") as zip_file:
            zip_file.extractall(self.paths.tool_root_directory)


class ToolCleaner:

    def __init__(self, tool: Tool) -> None:
        self.tool = tool
        self.paths = self.tool.get_paths()

    def clean(self) -> None:
        file_handler = FileHandler(self.paths.zipfile.parent)
        file_handler.delete_directory()

        file_handler.path = self.paths.temp_zipfile
        file_handler.delete_file_if_exists()
