import yaml
import subprocess
import requests
import shutil
from pathlib import Path
from pytoolbelt.environment.config import ProjectTree, PYTOOBELT_HOST
from pytoolbelt.core.exceptions import PythonEnvBuildError, PyEnvExistsError, MetaDataError
from pytoolbelt.core.bases import BaseTemplater


class PyEnv:

    def __init__(self, name: str, python_version: str) -> None:
        self.name = name
        self.python_version = python_version

    @property
    def metadata_path(self) -> Path:
        return ProjectTree.PYENVS_DIRECTORY / self.python_version

    def get_metadata(self) -> "PyEnvMetaData":
        return PyEnvMetaData(self)

    def get_builder(self) -> "PythonEnvBuilder":
        return PythonEnvBuilder(self)

    def get_downloader(self) -> "PyEnvDownloader":
        return PyEnvDownloader(self)

    def get_uploader(self) -> "PyEnvUploader":
        return PyEnvUploader(self)

    def get_templater(self) -> "PyEnvTemplater":
        return PyEnvTemplater(self)


class PyEnvMetaData:

    def __init__(self, pyenv: PyEnv) -> None:
        self.pyenv = pyenv

    @property
    def interpreter_install_path(self) -> Path:
        return ProjectTree.ENVIRONMENTS_DIRECTORY / self.pyenv.python_version / self.pyenv.name / f"venv"

    @property
    def meta_file_name(self) -> str:
        return f"{self.pyenv.name}.meta.yml"

    @property
    def env_meta_file(self) -> Path:
        return self.pyenv.metadata_path / self.meta_file_name

    def exists(self) -> None:
        if self.env_meta_file.exists():
            raise PyEnvExistsError(f"Python environment {self.pyenv.name} already exists")

    def save(self) -> None:
        self.pyenv.metadata_path.mkdir(exist_ok=True, parents=True)
        self.env_meta_file.touch(exist_ok=True)

    def get_metadata_config(self) -> "PyEnvMetaDataConfig":
        return PyEnvMetaDataConfig(self.env_meta_file)


class PyEnvMetaDataConfig:

    def __init__(self, pyenv_meta: Path) -> None:
        self.pyenv_meta = pyenv_meta
        self.data = None
        self.meta = None

    @property
    def name(self) -> str:
        return self.meta.get("name", "")

    @property
    def python_version(self) -> str:
        return self.meta.get("python_version", "")

    @property
    def requirements(self) -> list[str]:
        return self.meta.get("requirements", [])

    @property
    def description(self) -> str:
        return self.meta.get("description", "")

    def load(self) -> None:
        with self.pyenv_meta.open() as file:
            self.data = file.read()
            self.meta = yaml.safe_load(self.data)["env-meta"]

        self._validate()

    def _validate(self) -> None:

        if not self.meta or not self.data:
            raise MetaDataError(f"No metadata found for specified pyenv {self.pyenv_meta}")

        if not self.name:
            raise MetaDataError(f"A name must be provided for {self.pyenv_meta}")

        if not self.python_version:
            raise MetaDataError(f"A python version must be provided for {self.pyenv_meta}")

        if not self.requirements:
            raise MetaDataError(f"Requirements must be provided for {self.pyenv_meta}. If no requirements are needed, use the base pyenv")

        if not self.description:
            raise MetaDataError(f"A description must be provided for {self.pyenv_meta}")


class PyEnvDownloader:

    def __init__(self, pyenv: PyEnv) -> None:
        self.pyenv = pyenv

    @property
    def download_url(self) -> str:
        return f"{PYTOOBELT_HOST}/envs/{self.pyenv.python_version}/{self.pyenv.name}"

    def download(self) -> None:
        response = requests.get(self.download_url)

        if response.status_code != 200:
            raise PythonEnvBuildError(f"Failed to download python environment {self.pyenv.name}")

        self.pyenv.metadata_path.mkdir(exist_ok=True, parents=True)

        metadata = self.pyenv.get_metadata()
        metadata.env_meta_file.touch(exist_ok=True)
        metadata.env_meta_file.write_bytes(response.content)


class PyEnvUploader:

    def __init__(self, pyenv: PyEnv) -> None:
        self.pyenv = pyenv

    def upload(self) -> None:
        url = "http://localhost:8000/pyenv/post"

        metadata = self.pyenv.get_metadata()

        with metadata.env_meta_file.open() as file:
            data = yaml.safe_load(file.read())["env-meta"]
            response = requests.post(url, json=data)
        print(response.text)


class PythonEnvBuilder:

    def __init__(self, pyenv: PyEnv) -> None:
        self.pyenv = pyenv

    def build(self) -> None:
        metadata = self.pyenv.get_metadata()

        metadata.interpreter_install_path.mkdir(exist_ok=True, parents=True)

        command = [f"python{self.pyenv.python_version}", "-m", "venv", metadata.interpreter_install_path.as_posix(), "--clear"]
        result = subprocess.run(command)

        if result.returncode != 0:
            raise PythonEnvBuildError(f"Failed to build python environment {self.pyenv.name}")

        metadata_config = metadata.get_metadata_config()
        metadata_config.load()

        if metadata_config.requirements:
            self.install_requirements(metadata_config.requirements)

    def rebuild(self) -> None:
        if self.pyenv.get_metadata().interpreter_install_path.exists():
            shutil.rmtree(self.pyenv.get_metadata().interpreter_install_path)
        self.build()

    def install_requirements(self, requirements: list[str]) -> None:
        command = [
            self.pyenv.get_metadata().interpreter_install_path / "bin" / "pip",
            "install",
            *requirements,
        ]

        result = subprocess.run(command)

        if result.returncode != 0:
            raise PythonEnvBuildError(f"Failed to install requirements for python environment {self.pyenv.name}")


class PyEnvTemplater(BaseTemplater):

    def __init__(self, pyenv: PyEnv) -> None:
        super().__init__()
        self.pyenv = pyenv

    def template(self) -> None:
        self._template_pyenv_metadata_file()

    def _template_pyenv_metadata_file(self) -> None:
        template = self.jinja.get_template("pyenv.meta.yml.template")
        content = template.render(pyenv=self.pyenv)
        self.pyenv.get_metadata().env_meta_file.write_text(content)
