import yaml
import subprocess
from typing import Optional, List
from pathlib import Path
from semver import Version
from pydantic import BaseModel
from pytoolbelt.bases.base_paths import BasePaths
from pytoolbelt.bases.base_templater import BaseTemplater
from pytoolbelt.environment.config import PYTOOLBELT_PROJECT_ROOT, PYTOOLBELT_VENV_DIR
from pytoolbelt.core.exceptions import PythonEnvBuildError
from pytoolbelt.core.data_classes.name_version import NameVersion


class PtVenvConfig(BaseModel):
    name: str
    version: str
    python_version: str
    requirements: Optional[List[str]] = []
    ptvenv_hash: Optional[str] = None


class PtVenvPaths(BasePaths):

    def __init__(self, name_version: NameVersion, root_path: Optional[Path] = None) -> None:
        self._name_version = name_version
        super().__init__(root_path=root_path or PYTOOLBELT_PROJECT_ROOT, name=name_version.name, kind="ptvenv")

    @property
    def version(self) -> Version:
        return self._version

    @version.setter
    def version(self, version: Version) -> None:
        self._version = version

    @property
    def venv_def_root_dir(self) -> Path:
        return self.root_path / "ptvenv"

    @property
    def venv_def_dir(self) -> Path:
        return self.venv_def_root_dir / self.name

    @property
    def venv_def_file(self) -> Path:
        return self.venv_def_dir / f"{self.version}.yml"

    @property
    def new_directories(self) -> List[Path]:
        return [self.venv_def_dir]

    @property
    def new_files(self) -> List[Path]:
        return [self.venv_def_file]

    @property
    def install_path(self) -> Path:
        return PYTOOLBELT_VENV_DIR / self.name / str(self.version) / "venv"

    @property
    def executable_path(self) -> Path:
        return self.install_path / "bin" / "python"

    @property
    def pip_executable_path(self) -> Path:
        return self.install_path / "bin" / "pip"

    @property
    def release_tag(self) -> str:
        return f"{self.kind}-{self.name}-{str(self.version)}"

    def versions(self) -> List[Version]:
        versions = []
        for file in self.venv_def_dir.glob("*.yml"):
            try:
                version = Version.parse(file.stem)
            except ValueError:
                continue
            else:
                versions.append(version)
        versions.sort(reverse=True)
        return versions

    def set_highest_version(self) -> None:
        for file in self.venv_def_dir.glob(f"*.yml"):
            try:
                version = Version.parse(file.stem)
            except ValueError:
                continue
            else:
                if version > self._version:
                    self._version = version

    @staticmethod
    def get_venv_def_path(name: str, version: Version) -> Path:
        return PYTOOLBELT_PROJECT_ROOT / "venvdef" / name / f"{name}-{version}.yml"

    def get_venvdef(self) -> PtVenvConfig:
        with self.venv_def_file.open("r") as f:
            return PtVenvConfig(**yaml.safe_load(f))

    def raise_if_venvdef_exists(self) -> None:
        if self.venv_def_file.exists():
            raise FileExistsError(f"VenvDef file already exists: {self.venv_def_file}")

    def raise_if_venvdef_not_found(self) -> None:
        if not self.venv_def_file.exists():
            raise FileNotFoundError(f"VenvDef file not found: {self.venv_def_file}")


class PtVenvTemplater(BaseTemplater):
    def __init__(self, paths: PtVenvPaths):
        super().__init__()
        self.paths = paths

    def template_new_venvdef_file(self) -> None:
        template = self.render("venvdef.jinja2", name=self.paths.name, version=self.paths.version)
        with self.paths.venv_def_file.open("w") as f:
            f.write(template)


class PtVenvBuilder:
    def __init__(self, paths: PtVenvPaths):
        self.paths = paths
        self.venvdef = paths.get_venvdef()

    @property
    def create_command(self) -> List[str]:
        return [
            f"python{self.venvdef.python_version}",
            "-m",
            "venv",
            self.paths.install_path.as_posix(),
            "--clear"
        ]

    @property
    def install_requirements_command(self) -> List[str]:
        return [
            self.paths.pip_executable_path.as_posix(),
            "install",
            *self.venvdef.requirements
        ]

    def create_install_dir(self) -> None:
        self.paths.install_path.mkdir(parents=True, exist_ok=True)

    def install_requirements(self) -> None:

        result = subprocess.run(self.install_requirements_command)

        if result.returncode != 0:
            raise PythonEnvBuildError(f"Failed to install requirements for python environment {self.venvdef.name}")

    def build(self) -> None:
        self.create_install_dir()
        result = subprocess.run(self.create_command)

        if result.returncode != 0:
            raise PythonEnvBuildError(f"Failed to create the python virtual environment {self.venvdef.name}")

        if self.venvdef.requirements:
            self.install_requirements()


class PtVenv:

    def __init__(self, name_version: NameVersion) -> None:
        self._name_version = name_version
        self._paths = PtVenvPaths(name=name_version.name, version=name_version.version)
        self._templater = PtVenvTemplater(paths=self._paths)
        self._builder = PtVenvBuilder(paths=self._paths)

    @property
    def name(self) -> str:
        return self._name_version.name

    @property
    def version(self) -> Version:
        return self._name_version.version

    @property
    def paths(self) -> PtVenvPaths:
        return self._paths

    @property
    def templater(self) -> PtVenvTemplater:
        return self._templater

    @property
    def builder(self) -> PtVenvBuilder:
        return self._builder
