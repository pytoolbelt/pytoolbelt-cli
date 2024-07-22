import shutil
import subprocess
from pathlib import Path
from typing import List, Optional

import yaml
from pydantic import BaseModel
from semver import Version

from pytoolbelt.core.bases.base_paths import BasePaths
from pytoolbelt.core.bases.base_templater import BaseTemplater
from pytoolbelt.core.data_classes.component_metadata import ComponentMetadata
from pytoolbelt.core.data_classes.pytoolbelt_config import PytoolbeltConfig
from pytoolbelt.core.error_handling.exceptions import (
    PythonEnvBuildError,
    PytoolbeltError,
)
from pytoolbelt.core.tools import hash_config


class PtVenvConfig(BaseModel):
    class Config:
        arbitrary_types_allowed = True

    name: str
    version: Version
    python_version: str
    requirements: Optional[List[str]] = []

    @classmethod
    def from_file(cls, file_path: Path) -> "PtVenvConfig":
        with file_path.open("r") as f:
            raw_data = yaml.safe_load(f)
            raw_data["version"] = Version.parse(raw_data["version"])
            return cls(**raw_data)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "version": str(self.version),
            "python_version": self.python_version,
            "requirements": self.requirements,
        }


class IndentedSafeDumper(yaml.SafeDumper):
    def increase_indent(self, flow=False, indentless=False):
        return super(IndentedSafeDumper, self).increase_indent(flow, False)


class PtVenvPaths(BasePaths):
    def __init__(self, meta: ComponentMetadata, toolbelt_paths: "ToolbeltPaths") -> None:
        self._meta = meta
        self._toolbelt_paths = toolbelt_paths
        super().__init__(toolbelt_paths.root_path)

    @classmethod
    def from_tool_config(cls, tool_config: "ToolConfig", project_paths: "ProjectPaths") -> "PtVenvPaths":
        return cls(
            ComponentMetadata(name=tool_config.ptvenv.name, version=tool_config.ptvenv.version, kind="ptvenv"),
            project_paths,
        )

    @property
    def ptvenv_filename(self) -> str:
        return f"{self.meta.name}.yml"

    @property
    def ptvenv_hash_filename(self) -> str:
        return f"{self.meta.name}.sha256"

    @property
    def meta(self) -> ComponentMetadata:
        return self._meta

    @property
    def toolbelt_paths(self) -> "ToolbeltPaths":
        return self._toolbelt_paths

    @property
    def ptvenv_dir(self) -> Path:
        return self.toolbelt_paths.ptvenvs_dir / self.meta.name

    @property
    def ptvenv_config_file(self) -> Path:
        return self.ptvenv_dir / self.ptvenv_filename

    @property
    def ptvenv_readme_file(self) -> Path:
        return self.ptvenv_dir / "README.md"

    @property
    def new_directories(self) -> List[Path]:
        return [self.ptvenv_dir]

    @property
    def new_files(self) -> List[Path]:
        return [self.ptvenv_config_file, self.ptvenv_readme_file]

    @property
    def install_root_dir(self) -> Path:
        return self.toolbelt_paths.venv_install_dir / self.meta.name

    @property
    def install_version_dir(self) -> Path:
        return self.install_root_dir / str(self.meta.version)

    @property
    def install_dir(self) -> Path:
        return self.install_version_dir / "venv"

    @property
    def display_install_dir(self) -> str:
        return f"~/.pytoolbelt/environments/{self.meta.name}/{self.meta.version}"

    @property
    def installed_config_file(self) -> Path:
        return self.install_version_dir / self.ptvenv_filename

    @property
    def installed_hash_file(self) -> Path:
        return self.install_version_dir / self.ptvenv_hash_filename

    @property
    def python_executable_path(self) -> Path:
        return self.install_dir / "bin" / "python"

    @property
    def pip_executable_path(self) -> Path:
        return self.install_dir / "bin" / "pip"

    def raise_if_exists(self) -> None:
        if self.ptvenv_dir.exists():
            raise PytoolbeltError(f"ptvenv {self.meta.name} already exists.")

    def raise_if_ptvenv_is_not_installed(self) -> None:
        if not self.install_dir.exists():
            raise PytoolbeltError(f"ptvenv {self.meta.name} version {self.meta.version} is not installed.")

    def copy_config_to_install_dir(self) -> None:
        destination = self.install_version_dir / f"{self.meta.name}.yml"
        shutil.copy(self.ptvenv_config_file, destination)

    def list_installed_versions(self) -> List[Version]:
        if not self.install_root_dir.exists():
            return []
        versions = [Version.parse(d.name) for d in self.install_root_dir.iterdir() if Version.is_valid(d.name)]
        return sorted(versions, reverse=True)

    def get_latest_installed_version(self) -> Optional[Version]:
        try:
            return self.list_installed_versions()[0]
        except IndexError:
            return None

    def write_to_config_file(self, config: PtVenvConfig) -> None:
        with self.ptvenv_config_file.open("w") as f:
            yaml.dump(config.to_dict(), f, Dumper=IndentedSafeDumper, sort_keys=False, indent=2)


class PtVenvTemplater(BaseTemplater):
    def __init__(self, paths: PtVenvPaths):
        super().__init__()
        self.paths = paths

    def template_new_venvdef_file(self, ptc: PytoolbeltConfig) -> None:
        template = self.render("ptvenv_config.jinja2", meta=self.paths.meta, ptc=ptc)
        with self.paths.ptvenv_config_file.open("w") as f:
            f.write(template)


class PtVenvBuilder:
    def __init__(self, paths: PtVenvPaths):
        self.paths = paths
        self.ptvenv = None

    @property
    def create_command(self) -> List[str]:
        return [f"python{self.ptvenv.python_version}", "-m", "venv", self.paths.install_dir.as_posix(), "--clear"]

    @property
    def install_requirements_command(self) -> List[str]:
        return [self.paths.pip_executable_path.as_posix(), "install", *self.ptvenv.requirements]

    def load_config(self) -> None:
        self.ptvenv = PtVenvConfig.from_file(self.paths.ptvenv_config_file)

    def create_install_dir(self) -> None:
        self.paths.install_dir.mkdir(parents=True, exist_ok=True)

    def install_requirements(self) -> None:

        result = subprocess.run(self.install_requirements_command)

        if result.returncode != 0:
            self.remove_build_on_failure()
            raise PythonEnvBuildError(f"Failed to install requirements for python environment {self.ptvenv.name}")

    def remove_build_on_failure(self) -> None:
        if self.paths.install_version_dir.exists():
            shutil.rmtree(self.paths.install_version_dir)

    def build(self) -> None:
        self.load_config()
        self.create_install_dir()
        result = subprocess.run(self.create_command)

        if result.returncode != 0:
            self.remove_build_on_failure()
            raise PythonEnvBuildError(f"Failed to create the python virtual environment {self.ptvenv.name}")

        if self.ptvenv.requirements:
            self.install_requirements()

        self.paths.copy_config_to_install_dir()
        self.paths.installed_hash_file.write_text(hash_config(self.ptvenv))
