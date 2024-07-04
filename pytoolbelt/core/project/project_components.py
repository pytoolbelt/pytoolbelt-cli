from pathlib import Path
from typing import List, Optional

from pytoolbelt.bases.base_paths import BasePaths
from pytoolbelt.bases.base_templater import BaseTemplater
from pytoolbelt.core.data_classes.component_metadata import ComponentMetadata
from pytoolbelt.core.data_classes.pytoolbelt_config import RepoConfigs
from pytoolbelt.environment.config import (
    PYTOOLBELT_PROJECT_ROOT,
    PYTOOLBELT_VENV_INSTALL_DIR,
    PYTOOLBELT_TOOLS_INSTALL_DIR
)


class ProjectPaths(BasePaths):
    def __init__(self, project_root: Optional[Path] = None) -> None:
        project_root = project_root or PYTOOLBELT_PROJECT_ROOT
        super().__init__(root_path=project_root)

    @property
    def project_dir(self) -> Path:
        return self.root_path

    @property
    def ptvenvs_dir(self) -> Path:
        return self.project_dir / "ptvenv"

    @property
    def tools_dir(self) -> Path:
        return self.project_dir / "tools"

    @property
    def new_directories(self) -> List[Path]:
        return [self.ptvenvs_dir, self.tools_dir]

    @property
    def new_files(self) -> List[Path]:
        new_files = [self.gitignore, self.pytoolbelt_config]

        if self.dir_empty(self.ptvenvs_dir):
            new_files.append(self.ptvenvs_dir / ".gitkeep")

        if self.dir_empty(self.tools_dir):
            new_files.append(self.tools_dir / ".gitkeep")

        return new_files

    @property
    def gitignore(self) -> Path:
        return self.root_path / ".gitignore"

    @property
    def pytoolbelt_config(self) -> Path:
        return self.root_path / "pytoolbelt.yml"

    @property
    def git_dir(self) -> Path:
        return self.root_path / ".git"

    @property
    def venv_install_dir(self) -> Path:
        return PYTOOLBELT_VENV_INSTALL_DIR

    @property
    def tool_install_dir(self) -> Path:
        return PYTOOLBELT_TOOLS_INSTALL_DIR

    def get_pytoolbelt_config(self) -> RepoConfigs:
        raw_data = self.pytoolbelt_config.read_text()
        return RepoConfigs.from_yml(raw_data)

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

    # def get_ptvenv_defs_to_tag(self, local_tags: dict) -> List[PtVenvPaths]:
    #     to_tag = []
    #     for ptvenv_def in self.ptvenv_defs():
    #         for version in ptvenv_def.versions():
    #             try:
    #                 if version not in local_tags["ptvenv"][ptvenv_def.name]["versions"]:
    #                     to_tag.append(PtVenvPaths(ptvenv_def.name, version=version))
    #             except KeyError:
    #                 to_tag.append(PtVenvPaths(ptvenv_def.name, version=version))
    #     return to_tag
    #
    # def get_tools_to_tag(self, local_tags: dict) -> List[ToolPaths]:
    #     to_tag = []
    #     for tool in self.tools():
    #         try:
    #             if tool.version not in local_tags["tool"][tool.name]["versions"]:
    #                 to_tag.append(tool)
    #         except KeyError:
    #             to_tag.append(tool)
    #     return to_tag


class ProjectTemplater(BaseTemplater):
    def __init__(self, paths: ProjectPaths) -> None:
        super().__init__()
        self.paths = paths

    def template_new_project_files(self, overwrite: bool) -> None:
        for file in self.paths.new_files:
            if file.exists():
                if file.stat().st_size == 0 or overwrite:
                    self.write_template(file)

    def write_template(self, file: Path) -> None:
        template_name = self.format_template_name(file.name)
        rendered_template = self.render(template_name)
        with file.open("w") as f:
            f.write(rendered_template)
