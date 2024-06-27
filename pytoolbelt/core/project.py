from pathlib import Path
from typing import List
from pytoolbelt.bases.base_paths import BasePaths
from pytoolbelt.bases.base_templater import BaseTemplater
from pytoolbelt.core.ptvenv import PtVenvPaths
from pytoolbelt.core.tool import ToolPaths
from pytoolbelt.environment.config import PYTOOLBELT_TOOLS_ROOT, PYTOOLBELT_PTVENV_ROOT, PYTOOLBELT_PROJECT_ROOT
from pytoolbelt.core.pytoolbelt_config import RepoConfigs


class ProjectPaths(BasePaths):

    def __init__(self) -> None:
        super().__init__(root_path=PYTOOLBELT_PROJECT_ROOT, name="project", kind="project")

    @property
    def new_directories(self) -> List[Path]:
        return [self.ptvenvs_root, self.tools_root]

    @property
    def new_files(self) -> List[Path]:
        new_files = [self.gitignore, self.pytoolbelt_config]

        if self.dir_empty(self.ptvenvs_root):
            new_files.append(self.ptvenvs_root / ".gitkeep")

        if self.dir_empty(self.tools_root):
            new_files.append(self.tools_root / ".gitkeep")

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

    def ptvenv_defs(self) -> List[PtVenvPaths]:
        return [PtVenvPaths(d.name) for d in self.ptvenvs_root.iterdir() if d.is_dir()]

    def tools(self) -> List[ToolPaths]:
        return [ToolPaths(d.name, load_version=True) for d in self.tools_root.iterdir() if d.is_dir()]

    def get_pytoolbelt_config(self) -> RepoConfigs:
        raw_data = self.pytoolbelt_config.read_text()
        return RepoConfigs.from_yml(raw_data)

    def get_ptvenv_defs_to_tag(self, local_tags: dict) -> List[PtVenvPaths]:
        to_tag = []
        for ptvenv_def in self.ptvenv_defs():
            for version in ptvenv_def.versions():
                try:
                    if version not in local_tags["ptvenv"][ptvenv_def.name]["versions"]:
                        to_tag.append(PtVenvPaths(ptvenv_def.name, version=version))
                except KeyError:
                    to_tag.append(PtVenvPaths(ptvenv_def.name, version=version))
        return to_tag

    def get_tools_to_tag(self, local_tags: dict) -> List[ToolPaths]:
        to_tag = []
        for tool in self.tools():
            try:
                if tool.version not in local_tags["tool"][tool.name]["versions"]:
                    to_tag.append(tool)
            except KeyError:
                to_tag.append(tool)
        return to_tag


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
