import zipapp

import yaml

from pytoolbelt.bases.basepaths import BasePaths
from pathlib import Path
from typing import Optional, List
from pytoolbelt.environment.variables import PYTOOLBELT_PROJECT_ROOT
from semver import Version
from pytoolbelt.bases.basetemplater import BaseTemplater
from pydantic import BaseModel


class PtVenv(BaseModel):
    name: str
    version: str
    source: str


class ToolConfig(BaseModel):
    name: str
    version: str
    ptvenv: PtVenv


class ToolPaths(BasePaths):

    def __init__(self, name: str, root_path: Optional[Path] = None, version: Optional[Version] = None, load_version: Optional[bool] = False) -> None:
        super().__init__(root_path=root_path or PYTOOLBELT_PROJECT_ROOT, name=name, kind="tool")
        if version and load_version:
            raise ValueError("Cannot specify both version and load_version")

        self._version = version or Version.parse("0.0.0")

        if load_version:
            self.load_version_from_config()

    @property
    def version(self) -> Version:
        return self._version

    @version.setter
    def version(self, version: Version) -> None:
        self._version = version

    @property
    def tools_root_dir(self) -> Path:
        return self.root_path / "tools"

    @property
    def tool_dir(self) -> Path:
        return self.tools_root_dir / self.name

    @property
    def tool_code_dir(self) -> Path:
        return self.tool_dir / self.name

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
        return Path.home() / ".pytoolbelt" / "tools" / self.name

    @property
    def new_directories(self) -> List[Path]:
        return [
            self.tools_root_dir,
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
            self.cli_entrypoints_file
        ]

    @property
    def release_tag(self) -> str:
        return f"{self.kind}-{self.name}-{str(self.version)}"

    def get_tool_config(self) -> ToolConfig:
        with self.tool_config_file.open("r") as f:
            raw_yaml = yaml.safe_load(f)["tool"]
            ptvenv = PtVenv(**raw_yaml["ptvenv"])
            return ToolConfig(
                name=raw_yaml["name"],
                version=raw_yaml["version"],
                ptvenv=ptvenv
            )

    def load_version_from_config(self) -> None:
        config = self.get_tool_config()
        self.version = Version.parse(config.version)


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
                source=self.paths.tool_code_dir,
                target=target,
                interpreter=interpreter
            )
        self.paths.install_path.chmod(0o755)
