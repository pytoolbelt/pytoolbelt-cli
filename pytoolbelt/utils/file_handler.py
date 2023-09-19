import shutil
import yaml
from typing import Optional, Dict, Any
from pathlib import Path
from pytoolbelt.models.pyenv import PythonVersionEnum


class _NoAliasDumper(yaml.Dumper):
    def ignore_aliases(self, data):
        return True

    def increase_indent(self, flow=False, indentless=False):
        return super(_NoAliasDumper, self).increase_indent(flow, False)


# Add this after the NoAliasDumper definition
def enum_representer(dumper, data):
    return dumper.represent_scalar("tag:yaml.org,2002:str", data.value)


_NoAliasDumper.add_representer(PythonVersionEnum, enum_representer)


class FileHandler:

    def __init__(self, path: Path) -> None:
        self._path = path

    @property
    def path(self) -> Path:
        return self._path

    @path.setter
    def path(self, path: Path) -> None:
        self._path = path

    def is_file(self) -> None:
        return self.path.is_file() or self.path.suffix is not None

    def create_directory(self, parents: Optional[bool] = False) -> None:
        self.path.mkdir(exist_ok=True, parents=parents)

    def exists(self) -> bool:
        return self.path.exists()

    def create_file_if_not_exists(self) -> None:
        if self.is_file() and not self.exists():
            self.path.touch()

    def write_file(self, content: str) -> None:
        if self.path.is_file():
            self.path.write_text(content)
        else:
            raise FileNotFoundError(f"the path {str(self.path)} is not a file.")

    def write_file_if_not_exists(self, content: str) -> None:
        if self.is_file() and not self.exists():
            self.path.write_text(content)

    def read_file(self) -> str:
        return self.path.read_text()

    def delete_directory(self) -> None:
        shutil.rmtree(self.path)

    def delete_file_if_exists(self) -> None:
        if self.is_file() and self.exists():
            self.path.unlink()

    def write_yml_file(self, content: Dict[str, Any]) -> None:
        with self.path.open("w") as file:
            yaml.dump(content, file, Dumper=_NoAliasDumper, sort_keys=False)
