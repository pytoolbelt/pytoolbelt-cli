import subprocess
import yaml
from pydantic import BaseModel
from typing import List, Optional
from pytoolbelt.bases.base_paths import BasePaths
from pytoolbelt.core.data_classes.component_metadata import ComponentMetadata
from pathlib import Path
from pytoolbelt.bases.base_templater import BaseTemplater
from pytoolbelt.core.exceptions import PythonEnvBuildError


class PtVenvConfig(BaseModel):
    name: str
    version: str
    python_version: str
    requirements: Optional[List[str]] = []
    ptvenv_hash: Optional[str] = None

    @classmethod
    def from_file(cls, file_path: Path) -> "PtVenvConfig":
        with file_path.open("r") as f:
            raw_data = yaml.safe_load(f)
            return cls(**raw_data)


class PtVenvPaths(BasePaths):

    def __init__(self, meta: ComponentMetadata, project_paths: "ProjectPaths") -> None:
        self._meta = meta
        self._project_paths = project_paths
        super().__init__(project_paths.root_path)

    @property
    def meta(self) -> ComponentMetadata:
        return self._meta

    @property
    def project_paths(self) -> "ProjectPaths":
        return self._project_paths

    @property
    def ptvenv_dir(self) -> Path:
        return self.project_paths.ptvenv_dir / self.meta.name

    @property
    def ptvenv_config_file(self) -> Path:
        return self.ptvenv_dir / f"{self.meta.version}.yml"

    @property
    def new_directories(self) -> List[Path]:
        return [self.ptvenv_dir]

    @property
    def new_files(self) -> List[Path]:
        return [self.ptvenv_config_file]

    @property
    def install_dir(self) -> Path:
        return self.project_paths.venv_install_dir / self.meta.name / str(self.meta.version) / "venv"

    @property
    def python_executable_path(self) -> Path:
        return self.install_dir / "bin" / "python"

    @property
    def pip_executable_path(self) -> Path:
        return self.install_dir / "bin" / "pip"


class PtVenvTemplater(BaseTemplater):

    def __init__(self, paths: PtVenvPaths):
        super().__init__()
        self.paths = paths

    def template_new_venvdef_file(self) -> None:
        template = self.render("ptvenv_config.jinja2", meta=self.paths.meta)
        with self.paths.ptvenv_config_file.open("w") as f:
            f.write(template)


class PtVenvBuilder:

    def __init__(self, paths: PtVenvPaths):
        self.paths = paths
        self.ptvenv = PtVenvConfig.from_file(paths.ptvenv_config_file)

    @property
    def create_command(self) -> List[str]:
        return [
            f"python{self.ptvenv.python_version}",
            "-m",
            "venv",
            self.paths.install_dir.as_posix(),
            "--clear"
        ]

    @property
    def install_requirements_command(self) -> List[str]:
        return [
            self.paths.pip_executable_path.as_posix(),
            "install",
            *self.ptvenv.requirements
        ]

    def create_install_dir(self) -> None:
        self.paths.install_dir.mkdir(parents=True, exist_ok=True)

    def install_requirements(self) -> None:

        result = subprocess.run(self.install_requirements_command)

        if result.returncode != 0:
            raise PythonEnvBuildError(f"Failed to install requirements for python environment {self.ptvenv.name}")

    def build(self) -> None:
        self.create_install_dir()
        result = subprocess.run(self.create_command)

        if result.returncode != 0:
            raise PythonEnvBuildError(f"Failed to create the python virtual environment {self.ptvenv.name}")

        if self.ptvenv.requirements:
            self.install_requirements()
