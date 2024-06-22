from pathlib import Path
from typing import List
import yaml
import os
from pytoolbelt.bases.basepaths import BasePaths
from pytoolbelt.bases.basetemplater import BaseTemplater
from pytoolbelt.core.ptvenv import VenvDefPaths
from pytoolbelt.environment.variables import PYTOOLBELT_PROJECT_ROOT
from pytoolbelt.core.pytoolbelt_config import RepoConfigs


class ProjectPaths(BasePaths):

    def __init__(self) -> None:
        super().__init__(root_path=PYTOOLBELT_PROJECT_ROOT, name="project", kind="project")

    @property
    def venv_def_root_dir(self) -> Path:
        return VenvDefPaths.venv_def_root_dir

    @property
    def tool_def_root_dir(self) -> Path:
        pass

    @property
    def new_directories(self) -> List[Path]:
        return [self.venv_def_root_dir]

    @property
    def new_files(self) -> List[Path]:
        return [self.gitignore, self.pytoolbelt_config]

    @property
    def gitignore(self) -> Path:
        return self.root_path / ".gitignore"

    @property
    def pytoolbelt_config(self) -> Path:
        return self.root_path / "pytoolbelt.yml"

    @property
    def git_dir(self) -> Path:
        return self.root_path / ".git"

    def ptvenv_defs(self) -> List[VenvDefPaths]:
        return [VenvDefPaths(d.name) for d in self.venv_def_root_dir.iterdir() if d.is_dir()]

    def get_pytoolbelt_config(self) -> RepoConfigs:
        raw_data = self.pytoolbelt_config.read_text()
        return RepoConfigs.from_yml(raw_data)

    def get_ptvenv_defs_to_tag(self, local_tags: dict) -> List[VenvDefPaths]:
        to_tag = []
        for ptvenv_def in self.ptvenv_defs():
            for version in ptvenv_def.versions():
                try:
                    if version not in local_tags["ptvenv"][ptvenv_def.name]["versions"]:
                        to_tag.append(VenvDefPaths(ptvenv_def.name, version))
                except KeyError:
                    to_tag.append(VenvDefPaths(ptvenv_def.name, version))
        return to_tag


class ProjectTemplater(BaseTemplater):

    def __init__(self, paths: ProjectPaths) -> None:
        super().__init__()
        self.paths = paths

    def template_new_project_files(self, overwrite: bool) -> None:
        for file in self.paths.new_files:
            if not file.exists() or overwrite:
                self.write_template(file)

    def write_template(self, file: Path) -> None:
        template_name = self.format_template_name(file.name)
        rendered_template = self.render(template_name)
        with file.open("w") as f:
            f.write(rendered_template)
