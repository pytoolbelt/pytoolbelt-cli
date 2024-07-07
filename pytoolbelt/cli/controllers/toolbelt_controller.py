from pathlib import Path
from git import Repo
from pytoolbelt.core.data_classes.toolbelt_config import ToolbeltConfigs, ToolbeltConfig
from pytoolbelt.core.project.project_components import ProjectPaths
import giturlparse


class ToolbeltController:

    def __init__(self) -> None:
        self._toolbelt = ToolbeltConfigs.load()
        self._project_paths = ProjectPaths()

    @property
    def toolbelt(self) -> ToolbeltConfigs:
        return self._toolbelt

    @property
    def project_paths(self) -> ProjectPaths:
        return self._project_paths

    def _add_this_repo(self) -> int:
        repo = Repo(Path.cwd())
        self.project_paths.raise_if_not_pytoolbelt_project(repo)
        parsed_url = giturlparse.parse(repo.remotes.origin.url)

        if not parsed_url.valid:
            raise ValueError(f"Invalid git url: {repo.remotes.origin.url}")

        self.toolbelt.add(ToolbeltConfig.from_url(repo.remotes.origin.url))
        self.toolbelt.save()
        return 0

    def add(self, url: str, this_toolbelt: bool) -> int:
        if this_toolbelt:
            return self._add_this_repo()
        self.toolbelt.add(ToolbeltConfig.from_url(url))
        self.toolbelt.save()
        return 0
