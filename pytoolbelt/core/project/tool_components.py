import zipapp
from pathlib import Path
from typing import List, Optional

import yaml
from pydantic import BaseModel
from semver import Version

from pytoolbelt.bases.base_paths import BasePaths
from pytoolbelt.bases.base_templater import BaseTemplater
from pytoolbelt.core.data_classes.component_metadata import ComponentMetadata
from pytoolbelt.environment.config import PYTOOLBELT_PROJECT_ROOT


class PtVenv(BaseModel):
    name: str
    version: str


class ToolConfig(BaseModel):
    name: str
    version: str
    ptvenv: PtVenv

    @classmethod
    def from_file(cls, file: Path) -> "ToolConfig":
        with file.open("r") as f:
            raw_yaml = yaml.safe_load(f)["tool"]
            ptvenv = PtVenv(**raw_yaml["ptvenv"])
            return cls(name=raw_yaml["name"], version=raw_yaml["version"], ptvenv=ptvenv)


class ToolPaths(BasePaths):
    def __init__(self, meta: ComponentMetadata, project_paths: "ProjectPaths") -> None:
        self._meta = meta
        self._project_paths = project_paths
        super().__init__(project_paths.root_path)

    @property
    def project_paths(self) -> "ProjectPaths":
        return self._project_paths

    @property
    def meta(self) -> ComponentMetadata:
        return self._meta

    @property
    def tool_dir(self) -> Path:
        return self.project_paths.tools_dir / self.meta.name

    @property
    def tool_code_dir(self) -> Path:
        return self.tool_dir / self.meta.name

    @property
    def cli_dir(self) -> Path:
        return self.tool_code_dir / "cli"

    @property
    def tests_dir(self) -> Path:
        return self.tool_dir / "tests"

    @property
    def tool_config_file(self) -> Path:
        return self.tool_dir / "config.yml"

    @property
    def readme_md_file(self) -> Path:
        return self.tool_dir / "README.md"

    @property
    def dunder_main_file(self) -> Path:
        return self.tool_code_dir / "__main__.py"

    @property
    def dunder_cli_init_file(self) -> Path:
        return self.cli_dir / "__init__.py"

    @property
    def cli_entrypoints_file(self) -> Path:
        return self.cli_dir / "entrypoints.py"

    @property
    def install_path(self) -> Path:
        return Path.home() / ".pytoolbelt" / "tools" / self.meta.name

    @property
    def new_directories(self) -> List[Path]:
        return [
            self.tool_dir,
            self.tool_code_dir,
            self.cli_dir,
        ]

    @property
    def new_files(self) -> List[Path]:
        return [
            self.tool_config_file,
            self.readme_md_file,
            self.dunder_main_file,
            self.dunder_cli_init_file,
            self.cli_entrypoints_file,
        ]

    # TODO: this likely belongs somewhere else....
    # def get_tool_config(self) -> ToolConfig:
    #     with self.tool_config_file.open("r") as f:
    #         raw_yaml = yaml.safe_load(f)["tool"]
    #         ptvenv = PtVenv(**raw_yaml["ptvenv"])
    #         return ToolConfig(
    #             name=raw_yaml["name"],
    #             version=raw_yaml["version"],
    #             ptvenv=ptvenv
    #         )
    #
    # def load_version_from_config(self) -> None:
    #     config = self.get_tool_config()
    #     self.version = Version.parse(config.version)


class ToolTemplater(BaseTemplater):
    def __init__(self, paths: ToolPaths) -> None:
        super().__init__()
        self.paths = paths

    def template_new_tool_files(self) -> None:
        for file in self.paths.new_files:
            template_name = self.format_template_name(file.name)
            rendered = self.render(template_name, paths=self.paths)
            file.write_text(rendered)


class ToolInstaller:
    def __init__(self, paths: ToolPaths) -> None:
        self.paths = paths

    def install(self, interpreter: str) -> None:
        with self.paths.install_path.open("wb") as target:
            zipapp.create_archive(
                source=self.paths.tool_dir,
                target=target,
                interpreter=interpreter,
                main=self.paths.meta.name + ".__main__:main",
            )
        self.paths.install_path.chmod(0o755)
