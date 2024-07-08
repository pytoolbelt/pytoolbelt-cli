from pathlib import Path
from typing import Optional

import giturlparse
from git import Repo

from pytoolbelt.cli.views.toolbelt_views import ToolbeltConfigView
from pytoolbelt.core.data_classes.toolbelt_config import ToolbeltConfig, ToolbeltConfigs
from pytoolbelt.core.error_handling.exceptions import ToolbeltConfigNotFound
from pytoolbelt.core.project.toolbelt_components import ToolbeltPaths, ToolbeltTemplater
from pytoolbelt.core.tools.git_client import GitClient


class ToolbeltController:
    def __init__(self, root_path: Optional[Path] = None, **kwargs) -> None:
        self._project_paths = kwargs.get("paths", ToolbeltPaths(toolbelt_root=root_path))
        self.templater = kwargs.get("templater", ToolbeltTemplater(self._project_paths))
        self._toolbelt = ToolbeltConfigs.load()

    @property
    def toolbelt(self) -> ToolbeltConfigs:
        return self._toolbelt

    @property
    def project_paths(self) -> ToolbeltPaths:
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

    def create(self, **kwargs) -> int:
        # if we have provided a URL, add it to the toolbelt config
        if url := kwargs.get("url"):
            toolbelt_config = ToolbeltConfig.from_url(url)
        else:
            # we must have provided either a URL or name/owner
            toolbelt_config = ToolbeltConfig.from_name_owner(kwargs["name"], kwargs["owner"])

        self.toolbelt.add(toolbelt_config)
        self.project_paths.name = toolbelt_config.name
        self.project_paths.create()
        self.templater.template_new_toolbelt_files()
        repo = GitClient.init_if_not_exists(self.project_paths.toolbelt_dir)
        repo.create_remote(name="origin", url=toolbelt_config.url)
        self.toolbelt.save()
        return 0

    def add(self, url: str, this_toolbelt: bool) -> int:
        if this_toolbelt:
            return self._add_this_repo()
        self.toolbelt.add(ToolbeltConfig.from_url(url))
        self.toolbelt.save()
        return 0

    def remove(self, name: str) -> int:
        try:
            _ = self.toolbelt.repos.pop(name)
        except KeyError:
            raise ToolbeltConfigNotFound(f"Toolbelt {name} not found in config file.")
        else:
            self.toolbelt.save()
            return 0

    def show(self) -> int:
        table = ToolbeltConfigView()
        table.add_configs(self.toolbelt)
        table.print_table()
        return 0

    def fetch(self, name: str) -> int:
        try:
            toolbelt_config = self.toolbelt.repos[name]
        except KeyError:
            raise ToolbeltConfigNotFound(f"Toolbelt {name} not found in config file.")

        repo = GitClient.clone_from_url(toolbelt_config.url, self.project_paths.toolbelt_dir)
