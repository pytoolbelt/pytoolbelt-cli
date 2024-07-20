import zipapp
from pathlib import Path
from typing import List

import yaml
from pydantic import BaseModel

from pytoolbelt.core.bases.base_paths import BasePaths
from pytoolbelt.core.bases.base_templater import BaseTemplater
from pytoolbelt.core.data_classes.component_metadata import ComponentMetadata
from pytoolbelt.core.error_handling.exceptions import PytoolbeltError


class PtVenv(BaseModel):
    name: str
    version: str

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "version": self.version,
        }


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

    def to_dict(self) -> dict:
        return {
            "tool": {
                "name": self.name,
                "version": str(self.version),
                "ptvenv": self.ptvenv.to_dict(),
            }
        }


class IndentedSafeDumper(yaml.SafeDumper):
    def increase_indent(self, flow=False, indentless=False):
        return super(IndentedSafeDumper, self).increase_indent(flow, False)


class ToolPaths(BasePaths):
    def __init__(self, meta: ComponentMetadata, toolbelt_paths: "ToolbeltPaths") -> None:
        self._meta = meta
        self._toolbelt_paths = toolbelt_paths
        super().__init__(toolbelt_paths.root_path)

    @property
    def toolbelt_paths(self) -> "ToolbeltPaths":
        return self._toolbelt_paths

    @property
    def meta(self) -> ComponentMetadata:
        return self._meta

    @property
    def tool_dir(self) -> Path:
        return self.toolbelt_paths.tools_dir / self.meta.name

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
    def package_init_file(self) -> Path:
        return self.tool_code_dir / "__init__.py"

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
    def display_install_path(self) -> str:
        return f"~/.pytoolbelt/tools/{self.meta.name}"

    @property
    def zipapp_path(self) -> Path:
        return Path(f"{self.install_path.as_posix()}=={str(self.meta.version)}")

    @property
    def dev_install_path(self) -> Path:
        return Path(f"{self.install_path.as_posix()}-dev")

    @property
    def dev_symlink_path(self) -> Path:
        return self.install_path

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
            self.package_init_file,
            self.dunder_cli_init_file,
            self.cli_entrypoints_file,
        ]

    def create_install_symlink(self) -> None:
        if self.install_path.exists():
            self.install_path.unlink()
        self.install_path.symlink_to(self.zipapp_path)

    def create_dev_sym_link(self) -> None:
        if self.dev_symlink_path.exists():
            self.dev_symlink_path.unlink()
        self.dev_symlink_path.symlink_to(self.dev_install_path)

    def remove_installed_tool(self) -> None:
        self.install_path.unlink()
        self.zipapp_path.unlink()

    def remove_installed_dev_tool(self) -> None:
        self.dev_symlink_path.unlink()
        self.dev_install_path.unlink()

    def write_to_config_file(self, config: ToolConfig) -> None:
        with self.tool_config_file.open("w") as f:
            yaml.dump(config.to_dict(), f, Dumper=IndentedSafeDumper, sort_keys=False, indent=2)

    def raise_if_exists(self) -> None:
        if self.tool_dir.exists():
            raise PytoolbeltError(f"A tool named '{self.meta.name}' already exists in this project.")


class EntrypointShimTemplater(BaseTemplater):
    def __init__(self, tool_paths: ToolPaths, interpreter: str) -> None:
        self.tool_paths = tool_paths
        self.interpreter = interpreter
        super().__init__()

    def get_template_kwargs(self) -> dict:
        return {
            "python_executable": self.interpreter,
            "tool_path": self.tool_paths.tool_dir.as_posix(),
            "tool_name": self.tool_paths.meta.name,
        }

    def write_entrypoint_shim(self) -> None:
        content = self.render("entrypoint-shim.py.jinja2", **self.get_template_kwargs())
        self.tool_paths.dev_install_path.touch(exist_ok=True)
        self.tool_paths.dev_install_path.write_text(content)


class ToolTemplater(BaseTemplater):
    def __init__(self, paths: ToolPaths) -> None:
        super().__init__()
        self.paths = paths

    def template_new_tool_files(self) -> None:
        for file in self.paths.new_files:
            if file.parent.name == self.paths.meta.name and file.name == "__init__.py":
                continue
            template_name = self.format_template_name(file.name)
            rendered = self.render(template_name, paths=self.paths, name=self.paths.meta.name)
            file.write_text(rendered)


class ToolInstaller:
    def __init__(self, paths: ToolPaths) -> None:
        self.paths = paths

    def install(self, interpreter: str) -> int:
        with self.paths.zipapp_path.open("wb") as target:
            zipapp.create_archive(
                source=self.paths.tool_dir,
                target=target,
                interpreter=interpreter,
                main=self.paths.meta.name + ".__main__:main",
            )
        self.paths.create_install_symlink()
        self.paths.zipapp_path.chmod(0o755)
        return 0

    def install_shim(self, interpreter: str) -> int:
        shim_templater = EntrypointShimTemplater(self.paths, interpreter)
        shim_templater.write_entrypoint_shim()
        self.paths.create_dev_sym_link()
        self.paths.install_path.chmod(0o755)
        return 0
