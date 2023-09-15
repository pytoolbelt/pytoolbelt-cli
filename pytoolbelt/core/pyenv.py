import json
from hashlib import md5
from uuid import uuid4
import yaml
import string
import subprocess
from typing import List, Dict, Any, Optional
from pathlib import Path
from pytoolbelt.utils import file_handler, http_requests
from pytoolbelt.environment.config import ProjectTree, PYTOOBELT_HOST, DEFAULT_PYTHON_VERSION, STANDARD_PYENVS
from pytoolbelt.core.exceptions import PythonEnvBuildError, PyEnvExistsError, MetaDataError
from pytoolbelt.bases import BaseTemplater, BaseInitializer, BaseRemoteManager



class PyEnv:

    def __init__(self, name: str, python_version: str, uuid: Optional[str] = None) -> None:
        self.name = name
        self.python_version = python_version
        self.uuid = uuid
        self.__json_payload = {}

    @classmethod
    def from_id(cls, pyenv_id: str) -> "PyEnv":
        return cls(name="", python_version="", uuid=pyenv_id)

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "PyEnv":

        obj = cls(
            name=data["name"],
            python_version=data["python_version"],
            uuid=data["pyenv_id"]
        )

        obj.__json_payload["env-meta"] = data
        return obj

    @staticmethod
    def generate_id() -> str:
        return str(uuid4())

    def get_metadata(self) -> "PyEnvMetaData":
        if not self.__json_payload:
            return PyEnvMetaData(self)
        return PyEnvMetaData.from_json(self.__json_payload)

    def get_builder(self) -> "PyEnvBuilder":
        return PyEnvBuilder(self)

    def get_pyenv_remote_manager(self) -> "PyEnvRemoteManager":
        return PyEnvRemoteManager(self)

    def get_initializer(self) -> "PyEnvInitializer":
        return PyEnvInitializer(self)

    def get_templater(self) -> "PyEnvTemplater":
        return PyEnvTemplater(self)

    def get_hasher(self) -> "PyEnvHasher":
        return PyEnvHasher(self)


class PyEnvMetaData:

    def __init__(self, pyenv: PyEnv) -> None:
        self.pyenv = pyenv
        self.data = {}
        self.meta = {}
        self._md5_hash = None

    @classmethod
    def from_json(cls, data: Dict[str, Any]) -> "PyEnvMetaData":
        obj = cls(pyenv=PyEnv.from_json(data["env-meta"]))
        obj.data = data
        obj.meta = data["env-meta"]

        for key, value in obj.meta.items():
            setattr(obj, key, value)
        return obj

    @property
    def metadata_path(self) -> Path:
        return ProjectTree.PYENVS_DIRECTORY / self.python_version

    @property
    def interpreter_install_path(self) -> Path:
        return ProjectTree.ENVIRONMENTS_DIRECTORY / self.python_version / self.pyenv.name / f"venv"

    @property
    def pyenv_meta_file_name(self) -> str:
        return f"{self.pyenv.name}.meta.yml"

    @property
    def pyenv_env_meta_file(self) -> Path:
        return self.metadata_path / self.pyenv_meta_file_name

    @property
    def name(self) -> str:
        return self.meta.get("name", "")

    @name.setter
    def name(self, value: str) -> None:
        self.meta["name"] = value

    @property
    def pyenv_id(self) -> str:
        return self.meta.get("pyenv_id", "")

    @pyenv_id.setter
    def pyenv_id(self, value: str) -> None:
        self.meta["pyenv_id"] = value

    @property
    def python_version(self) -> str:
        return self.meta.get("python_version", DEFAULT_PYTHON_VERSION)

    @python_version.setter
    def python_version(self, value: str) -> None:
        self.meta["python_version"] = value

    @property
    def requirements(self) -> list[str]:
        return self.meta.get("requirements", [])

    @requirements.setter
    def requirements(self, value: list[str]) -> None:
        self.meta["requirements"] = value

    @property
    def description(self) -> str:
        return self.meta.get("description", "")

    @description.setter
    def description(self, value: str) -> None:
        self.meta["description"] = value

    @property
    def md5_hash(self) -> str:
        return self._md5_hash

    @md5_hash.setter
    def md5_hash(self, value: str) -> None:
        self._md5_hash = value

    def raise_if_exists(self) -> None:
        if file_handler.check_exists(self.pyenv_env_meta_file):
            raise PyEnvExistsError(f"Python environment {self.pyenv.name} already exists.")

    def get_json_payload(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "pyenv_id": self.pyenv_id,
            "python_version": self.python_version,
            "requirements": self.requirements,
            "description": self.description,
            "md5_hash": self.md5_hash
        }

    def get_raw_metadata(self) -> str:
        return file_handler.read_file(self.pyenv_env_meta_file)

    def load(self) -> None:
        self.data = self.get_raw_metadata()
        self.meta = yaml.safe_load(self.data)["env-meta"]
        self._validate()

    def _validate(self) -> None:

        if not self.meta or not self.data:
            raise MetaDataError(f"No metadata found for specified pyenv {self.pyenv.name}")

        if not self.name:
            raise MetaDataError(f"A name must be provided for {self.pyenv.name}")

        if not self.python_version:
            raise MetaDataError(f"A python version must be provided for {self.pyenv.name}")

        if not self.requirements:
            raise MetaDataError(
                f"Requirements must be provided for {self.pyenv.name}. If no requirements are needed, use the base pyenv")

        if not self.description:
            raise MetaDataError(f"A description must be provided for {self.pyenv.name}")


class PyEnvInitializer(BaseInitializer):

    def __init__(self, pyenv: PyEnv) -> None:
        super().__init__()
        self.pyenv = pyenv
        self.pyenv_metadata = pyenv.get_metadata()

    @property
    def files(self) -> List[Path]:
        return [
            self.pyenv_metadata.pyenv_env_meta_file
        ]

    @property
    def directories(self) -> List[Path]:
        return [
            self.pyenv_metadata.metadata_path,
            self.pyenv_metadata.interpreter_install_path
        ]


class PyEnvTemplater(BaseTemplater):

    def __init__(self, pyenv: PyEnv) -> None:
        super().__init__()
        self.pyenv = pyenv
        self.pyenv_metadata = self.pyenv.get_metadata()

    def _get_template_filename(self) -> str:
        if self.pyenv.name not in STANDARD_PYENVS:
            return "pyenv.meta.yml.template"
        return f"{self.pyenv.name}.meta.yml.template"

    def _template_pyenv_metadata_file(self) -> None:
        template_filename = self._get_template_filename()
        template = self.jinja.get_template(template_filename)
        content = template.render(pyenv=self.pyenv)
        file_handler.write_file(self.pyenv_metadata.pyenv_env_meta_file, content)


class PyEnvRemoteManager(BaseRemoteManager):

    def __init__(self, pyenv: PyEnv) -> None:
        super().__init__()
        self.pyenv = pyenv

    @property
    def download_url(self) -> str:
        return f"{PYTOOBELT_HOST}/pyenv/get/{self.pyenv.uuid}"

    @property
    def upload_url(self) -> str:
        return f"{PYTOOBELT_HOST}/pyenv/create"

    def download(self) -> None:
        response = http_requests.get_pyenv_metadata(self.download_url)

        pyenv = PyEnv.from_json(response.json())
        metadata = pyenv.get_metadata()

        file_handler.write_yml_file(metadata.pyenv_env_meta_file, metadata.data)

    def upload(self) -> None:
        hasher = self.pyenv.get_hasher()
        payload = hasher.get_payload()
        _ = http_requests.post_pyenv_metadata(payload, self.upload_url)


class PyEnvHasher:

    def __init__(self, pyenv: PyEnv) -> None:
        self.pyenv = pyenv

    def get_payload(self) -> Dict[str, Any]:
        metadata = self.pyenv.get_metadata()
        metadata.load()
        metadata.md5_hash = self._hash_metadata()
        return metadata.get_json_payload()

    def _hash_metadata(self) -> str:
        data = self._serialize_metadata()
        data = self._strip_whitespace(data)
        data = self._make_lowercase(data)
        return md5(data.encode()).hexdigest()

    def _serialize_metadata(self) -> str:
        metadata = self.pyenv.get_metadata()
        metadata.load()
        return json.dumps(metadata.data)

    @staticmethod
    def _strip_whitespace(raw_config: str) -> str:
        return raw_config.translate({ord(c): None for c in string.whitespace})

    @staticmethod
    def _make_lowercase(raw_config: str) -> str:
        return raw_config.lower()


class PyEnvBuilder:

    def __init__(self, pyenv: PyEnv) -> None:
        self.pyenv = pyenv

    def build(self) -> None:
        metadata = self.pyenv.get_metadata()
        metadata.load()

        command = [
            f"python{self.pyenv.python_version}",
            "-m",
            "venv",
            metadata.interpreter_install_path.as_posix(),
            "--clear"
        ]
        result = subprocess.run(command)

        if result.returncode != 0:
            raise PythonEnvBuildError(f"Failed to build python environment {self.pyenv.name}")

        if metadata.requirements:
            self.install_requirements(metadata.requirements)

    def rebuild(self) -> None:
        metadata = self.pyenv.get_metadata()
        if file_handler.check_exists(metadata.interpreter_install_path):
            file_handler.delete_directory(metadata.interpreter_install_path)
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
