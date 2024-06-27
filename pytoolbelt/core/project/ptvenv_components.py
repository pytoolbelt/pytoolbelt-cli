from pydantic import BaseModel
from typing import List, Optional
from pytoolbelt.bases.base_paths import BasePaths
from pytoolbelt.core.data_classes.name_version import NameVersion
from pathlib import Path


class PtVenvConfig(BaseModel):
    name: str
    version: str
    python_version: str
    requirements: Optional[List[str]] = []
    ptvenv_hash: Optional[str] = None


class PtVenvPaths(BasePaths):

    def __init(self, meta: NameVersion, project_paths: "ProjectPaths") -> None:
        self._meta = meta
        self._project_paths = project_paths
        super().__init__(project_paths.root_path)

    @property
    def meta(self) -> NameVersion:
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
