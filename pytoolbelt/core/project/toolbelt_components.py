from pathlib import Path
from typing import Iterator, List, Optional

import giturlparse
from git import Repo

from pytoolbelt.core.bases.base_paths import BasePaths
from pytoolbelt.core.bases.base_templater import BaseTemplater
from pytoolbelt.core.data_classes.component_metadata import ComponentMetadata
from pytoolbelt.core.data_classes.toolbelt_config import ToolbeltConfigs
from pytoolbelt.core.error_handling.exceptions import PytoolbeltError
from pytoolbelt.environment.config import (
    PYTOOLBELT_TOOLBELT_CONFIG_FILE,
    PYTOOLBELT_TOOLBELT_INSTALL_DIR,
    PYTOOLBELT_TOOLBELT_ROOT,
    PYTOOLBELT_TOOLS_INSTALL_DIR,
    PYTOOLBELT_VENV_INSTALL_DIR,
)


class ToolbeltPaths(BasePaths):
    def __init__(self, toolbelt_root: Optional[Path] = None) -> None:
        toolbelt_root = toolbelt_root or PYTOOLBELT_TOOLBELT_ROOT
        super().__init__(root_path=toolbelt_root)

    @property
    def toolbelt_dir(self) -> Path:
        return self.root_path

    @property
    def ptvenvs_dir(self) -> Path:
        return self.toolbelt_dir / "ptvenv"

    @property
    def tools_dir(self) -> Path:
        return self.toolbelt_dir / "tools"

    @property
    def new_directories(self) -> List[Path]:
        return [
            self.ptvenvs_dir,
            self.tools_dir,
            self.venv_install_dir,
            self.toolbelt_install_dir,
            self.tool_install_dir,
        ]

    @property
    def new_files(self) -> List[Path]:
        new_files = [self.gitignore, self.pytoolbelt_config, self.global_config_file]

        if self.dir_empty(self.ptvenvs_dir):
            new_files.append(self.ptvenvs_dir / ".gitkeep")

        if self.dir_empty(self.tools_dir):
            new_files.append(self.tools_dir / ".gitkeep")

        return new_files

    @property
    def gitignore(self) -> Path:
        return self.toolbelt_dir / ".gitignore"

    @property
    def global_config_file(self) -> Path:
        return PYTOOLBELT_TOOLBELT_CONFIG_FILE

    @property
    def pytoolbelt_config(self) -> Path:
        return self.toolbelt_dir / "pytoolbelt.yml"

    @property
    def git_dir(self) -> Path:
        return self.toolbelt_dir / ".git"

    @property
    def venv_install_dir(self) -> Path:
        return PYTOOLBELT_VENV_INSTALL_DIR

    @property
    def tool_install_dir(self) -> Path:
        return PYTOOLBELT_TOOLS_INSTALL_DIR

    @property
    def toolbelt_install_root_dir(self) -> Path:
        return PYTOOLBELT_TOOLBELT_INSTALL_DIR

    @property
    def toolbelt_install_dir(self) -> Path:
        return self.toolbelt_install_root_dir

    def is_pytoolbelt_project(self) -> bool:
        if self.git_dir.exists():
            if self.pytoolbelt_config.exists():
                if self.tools_dir.exists():
                    if self.ptvenvs_dir.exists():
                        return True
        return False

    def raise_if_not_pytoolbelt_project(self) -> None:
        if not self.is_pytoolbelt_project():
            raise PytoolbeltError("This directory is not the root of a pytoolbelt project.")

    def raise_if_exists(self) -> None:
        if self.toolbelt_install_dir.exists():
            raise PytoolbeltError(
                f"Toolbelt not found at {self.toolbelt_install_dir}. Try fetching or creating a new toolbelt."
            )

    def raise_if_not_exists(self) -> None:
        if not self.toolbelt_install_dir.exists():
            raise PytoolbeltError(
                f"Toolbelt not found at {self.toolbelt_install_dir}. Try fetching or creating a new toolbelt."
            )

    def get_pytoolbelt_config(self) -> ToolbeltConfigs:
        raw_data = self.pytoolbelt_config.read_text()
        return ToolbeltConfigs.from_yml(raw_data)

    def iter_tools(self) -> Iterator[str]:
        for tool in self.tools_dir.iterdir():
            if tool.is_dir():
                yield tool.name

    def iter_ptvenvs(self) -> Iterator[str]:
        for ptvenv in self.ptvenvs_dir.iterdir():
            if ptvenv.is_dir():
                yield ptvenv.name

    def iter_installed_ptvenvs(self, name: Optional[str] = None) -> List[ComponentMetadata]:
        for venv in self.venv_install_dir.iterdir():
            if venv.is_dir():
                for version in venv.iterdir():
                    if version.is_dir():
                        if name and venv.name == name:
                            yield ComponentMetadata(venv.name, version.name, "ptvenv")
                        yield ComponentMetadata(venv.name, version.name, "ptvenv")

    def iter_installed_tools(self) -> List[ComponentMetadata]:
        for tool in self.tool_install_dir.iterdir():
            if tool.is_symlink():
                links_to = tool.readlink().name
                if links_to.endswith("dev"):
                    yield ComponentMetadata(f"{tool.name} (dev-mode)", "latest", "tool")
                else:
                    yield ComponentMetadata.from_string(links_to, "tool")


class ToolbeltTemplater(BaseTemplater):
    def __init__(self, paths: ToolbeltPaths) -> None:
        super().__init__()
        self.paths = paths

    def template_new_toolbelt_files(self) -> None:
        for file in self.paths.new_files:
            if file.exists():
                if file.stat().st_size == 0:
                    self.write_template(file)

    def write_template(self, file: Path) -> None:
        template_name = self.format_template_name(file.name)
        rendered_template = self.render(template_name)
        with file.open("w") as f:
            f.write(rendered_template)
