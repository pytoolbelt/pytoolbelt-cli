import shutil
import yaml
from pathlib import Path
from pytoolbelt.models.pyenv import PythonVersionEnum


class NoAliasDumper(yaml.Dumper):
    def ignore_aliases(self, data):
        return True

    def increase_indent(self, flow=False, indentless=False):
        return super(NoAliasDumper, self).increase_indent(flow, False)


# Add this after the NoAliasDumper definition
def enum_representer(dumper, data):
    return dumper.represent_scalar("tag:yaml.org,2002:str", data.value)


NoAliasDumper.add_representer(PythonVersionEnum, enum_representer)


def create_directory(path: Path, parents: bool = False) -> None:
    path.mkdir(exist_ok=True, parents=parents)


def check_exists(path: Path) -> bool:
    return path.exists()


def create_file_if_not_exists(path: Path) -> None:
    if not check_exists(path):
        path.touch()


def write_file(path: Path, content, mode: str = "w") -> None:
    with path.open(mode) as file:
        file.write(content)


def write_file_if_not_exists(path: Path, content, mode: str = "w") -> None:
    if not check_exists(path):
        with path.open(mode) as file:
            file.write(content)


def read_file(path: Path, mode: str = "r") -> str:
    with path.open(mode) as file:
        return file.read()


def delete_directory(path: Path) -> None:
    shutil.rmtree(path)


def delete_file_if_exists(path: Path) -> None:
    if check_exists(path):
        path.unlink()


def write_yml_file(path: Path, content: dict) -> None:
    with path.open("w") as file:
        yaml.dump(content, file, Dumper=NoAliasDumper, sort_keys=False)
