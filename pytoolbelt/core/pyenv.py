import subprocess
import shutil
from pathlib import Path
from typing import List
from pytoolbelt.core.project import ProjectPaths
from pytoolbelt.bases.creator import BaseCreator
from pytoolbelt.core.exceptions import PyEnvExistsError
from pytoolbelt.models.pyenv import PyEnvModel
from pytoolbelt.model_utils.pyenv import PyEnvModelFactory, PyEnvModelHasher
from pytoolbelt.utils.file_handler import FileHandler
from pytoolbelt.core.exceptions import PythonEnvBuildError


class PyEnv:

    def __init__(self, name: str, python_version: str) -> None:
        self._name = name
        self._python_version = python_version
        self._project_paths = ProjectPaths()

    @classmethod
    def from_name(cls, name: str) -> "PyEnv":
        project_paths = ProjectPaths()
        pyenv_model = PyEnvModelFactory.from_path(project_paths.pyenvs / f"{name}.yml")
        return cls(pyenv_model.name, pyenv_model.python_version)

    @property
    def name(self) -> str:
        return self._name

    @property
    def python_version(self) -> str:
        return self._python_version

    @property
    def project_paths(self) -> ProjectPaths:
        return self._project_paths

    def get_paths(self) -> "PyEnvPaths":
        return PyEnvPaths(self)

    def get_creator(self) -> "PyEnvCreator":
        return PyEnvCreator(self)

    def get_writer(self) -> "PyEnvWriter":
        return PyEnvWriter(self)

    def get_destroyer(self) -> "PyEnvDestroyer":
        return PyEnvDestroyer(self)

    def get_builder(self) -> "PyEnvBuilder":
        return PyEnvBuilder(self)


class PyEnvPaths:

    def __init__(self, pyenv: PyEnv) -> None:
        self.pyenv = pyenv

    @property
    def pyenv_definitions_directory(self) -> Path:
        return self.pyenv.project_paths.pyenvs

    @property
    def pyenv_definition_file(self) -> Path:
        return self.pyenv_definitions_directory / f"{self.pyenv.name}.yml"

    @property
    def interpreter_install_path(self) -> Path:
        return self.pyenv.project_paths.environments / self.pyenv.name / "venv"

    @property
    def pyenv_metadata_file(self) -> Path:
        return self.interpreter_install_path.parent / f"{self.pyenv.name}.yml"

    @property
    def pip_path(self) -> Path:
        return self.interpreter_install_path / "bin" / "pip"


class PyEnvCreator(BaseCreator):

    def __init__(self, pyenv: PyEnv) -> None:
        self.pyenv = pyenv
        self.paths = pyenv.get_paths()

    @property
    def directories(self) -> list[Path]:
        return [
            self.paths.pyenv_definitions_directory,
            self.paths.interpreter_install_path
        ]

    @property
    def files(self) -> list[Path]:
        return [
            self.paths.pyenv_definition_file
        ]

    def _exists(self) -> None:
        if self.paths.pyenv_definition_file.exists():
            raise PyEnvExistsError(f"{self.pyenv.name} already exists.")


class PyEnvWriter:

    def __init__(self, pyenv: PyEnv) -> None:
        self.pyenv = pyenv

    def write(self) -> None:
        pyenv_model = PyEnvModelFactory.new(self.pyenv.name, self.pyenv.python_version)
        paths = self.pyenv.get_paths()

        file_handler = FileHandler(paths.pyenv_definition_file)

        content = pyenv_model.model_dump()
        content.pop("md5_hash")
        file_handler.write_yml_file(content=content)


class PyEnvDestroyer:

    def __init__(self, pyenv: PyEnv) -> None:
        self.pyenv = pyenv

    def destroy(self) -> None:
        paths = self.pyenv.get_paths()

        file_handler = FileHandler(paths.pyenv_definition_file)
        file_handler.delete_file_if_exists()

        file_handler.path = paths.interpreter_install_path
        file_handler.delete_directory()


class PyEnvBuilder:

    def __init__(self, pyenv: PyEnv) -> None:
        self.pyenv = pyenv

    def build(self) -> None:
        paths = self.pyenv.get_paths()
        pyenv_model = PyEnvModelFactory.from_path(paths.pyenv_definition_file)

        command = [
            f"python{pyenv_model.python_version}",
            "-m",
            "venv",
            paths.interpreter_install_path.as_posix(),
            "--clear"
        ]
        result = subprocess.run(command)

        if result.returncode != 0:
            raise PythonEnvBuildError(f"Failed to build python environment {self.pyenv.name}")

        if pyenv_model.requirements:
            self.install_requirements(paths, pyenv_model.requirements)

        self.copy_metadata(paths, pyenv_model)

    def install_requirements(self, paths: PyEnvPaths, requirements: List[str]) -> None:

        command = [
            paths.pip_path.as_posix(),
            "install",
            *requirements,
        ]

        result = subprocess.run(command)

        if result.returncode != 0:
            raise PythonEnvBuildError(f"Failed to install requirements for python environment {self.pyenv.name}")

    @staticmethod
    def copy_metadata(paths: PyEnvPaths, pyenv_model: PyEnvModel) -> None:

        hasher = PyEnvModelHasher(pyenv_model)
        pyenv_model = hasher.hash()

        file_handler = FileHandler(paths.pyenv_metadata_file)
        file_handler.write_yml_file(content=pyenv_model.model_dump())
