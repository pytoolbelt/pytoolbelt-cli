import yaml
import subprocess
import hashlib
from typing import Optional, List
from pathlib import Path
from semver import Version
from pydantic import BaseModel
from pytoolbelt.bases.basepaths import BasePaths
from pytoolbelt.bases.basetemplater import BaseTemplater
from pytoolbelt.environment.variables import PYTOOLBELT_PROJECT_ROOT, PYTOOLBELT_VENV_DIR
from pytoolbelt.core.exceptions import PythonEnvBuildError


class VenvDef(BaseModel):
    name: str
    version: str
    python_version: str
    requirements: Optional[List[str]] = []
    ptvenv_hash: Optional[str] = None

    def get_sha256(self) -> str:
        return hashlib.sha256(str(self).encode()).hexdigest()

    def generate_hash(self) -> None:
        self.ptvenv_hash = self.get_sha256()


class VenvDefPaths(BasePaths):

    venv_def_root_dir: Path = PYTOOLBELT_PROJECT_ROOT / "venvdef"

    def __init__(self, name: str, version: Optional[Version] = None):
        self._version = version or Version.parse("0.0.0")
        super().__init__(root_path=PYTOOLBELT_PROJECT_ROOT, name=name)

    @property
    def version(self) -> Version:
        return self._version

    @version.setter
    def version(self, version: Version) -> None:
        self._version = version

    @property
    def venv_def_dir(self) -> Path:
        return self.venv_def_root_dir / self.name

    @property
    def venv_def_file(self) -> Path:
        return self.venv_def_dir / f"{self.name}-{self.version}.yml"

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
    def pip_executable_path(self) -> Path:
        return self.install_path / "bin" / "pip"

    def set_highest_version(self) -> None:
        for file in self.venv_def_dir.glob(f"{self.name}-*.yml"):
            version = Version.parse(file.stem.split("-")[-1])
            if version > self._version:
                self._version = version

    @staticmethod
    def get_venv_def_path(name: str, version: Version) -> Path:
        return PYTOOLBELT_PROJECT_ROOT / "venvdef" / name / f"{name}-{version}.yml"

    def get_venvdef(self) -> VenvDef:
        with self.venv_def_file.open("r") as f:
            return VenvDef(**yaml.safe_load(f))

    def raise_if_venvdef_exists(self) -> None:
        if self.venv_def_file.exists():
            raise FileExistsError(f"VenvDef file already exists: {self.venv_def_file}")

    def raise_if_venvdef_not_found(self) -> None:
        if not self.venv_def_file.exists():
            raise FileNotFoundError(f"VenvDef file not found: {self.venv_def_file}")


class VenvDefTemplater(BaseTemplater):
    def __init__(self, paths: VenvDefPaths):
        super().__init__()
        self.paths = paths

    def template_new_venvdef_file(self) -> None:
        template = self.render("venvdef.jinja2", name=self.paths.name, version=self.paths.version)
        with self.paths.venv_def_file.open("w") as f:
            f.write(template)


class VenvBuilder:
    def __init__(self, paths: VenvDefPaths):
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
