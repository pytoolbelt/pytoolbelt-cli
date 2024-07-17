from pathlib import Path
from typing import Optional

import giturlparse
from git import Repo

from pytoolbelt.cli.views.toolbelt_views import ToolbeltConfigView
from pytoolbelt.core.data_classes.toolbelt_config import ToolbeltConfig, ToolbeltConfigs
from pytoolbelt.core.error_handling.exceptions import (
    ToolbeltConfigNotFound,
    ToolbeltExistsError,
)
from pytoolbelt.core.project.toolbelt_components import ToolbeltPaths, ToolbeltTemplater
from pytoolbelt.core.tools.git_client import GitClient
from pytoolbelt.environment.config import PYTOOLBELT_TOOLBELT_INSTALL_DIR


class ToolbeltController:
    def __init__(self, root_path: Optional[Path] = None, **kwargs) -> None:
        self._toolbelt_paths = kwargs.get("paths", ToolbeltPaths(toolbelt_root=root_path))
        self.templater = kwargs.get("templater", ToolbeltTemplater(self._toolbelt_paths))
        self._toolbelt = ToolbeltConfigs.load()

    @property
    def toolbelt(self) -> ToolbeltConfigs:
        return self._toolbelt

    @property
    def toolbelt_paths(self) -> ToolbeltPaths:
        return self._toolbelt_paths

    def _add_this_repo(self) -> int:
        repo = Repo(Path.cwd())
        self.toolbelt_paths.raise_if_not_pytoolbelt_project(repo)
        parsed_url = giturlparse.parse(repo.remotes.origin.url)

        if not parsed_url.valid:
            raise ValueError(f"Invalid git url: {repo.remotes.origin.url}")

        toolbelt_config = ToolbeltConfig.from_url(repo.remotes.origin.url, self.toolbelt_paths.toolbelt_dir.as_posix())
        self.toolbelt.add(toolbelt_config)
        self.toolbelt.save()
        return 0

    def create(self, **kwargs) -> int:
        # if we have provided a URL, add it to the toolbelt config

        toolbelt_paths = ToolbeltPaths(toolbelt_root=PYTOOLBELT_TOOLBELT_INSTALL_DIR)

        if url := kwargs.get("url"):
            toolbelt_config = ToolbeltConfig.from_url(url)
        else:
            # we must have provided either a URL or name/owner
            toolbelt_config = ToolbeltConfig.from_name_owner(kwargs["name"], kwargs["owner"])

        # set the path to the toolbelt directory. Name must be set in the project
        toolbelt_paths.name = toolbelt_config.name
        toolbelt_config.path = toolbelt_paths.toolbelt_dir.as_posix()

        if toolbelt_paths.toolbelt_dir.exists():
            raise ToolbeltExistsError(f"Toolbelt {toolbelt_config.name} already exists.")

        self.toolbelt.add(toolbelt_config)

        toolbelt_paths.create()
        self.templater.paths = toolbelt_paths
        self.templater.template_new_toolbelt_files()
        repo = GitClient.init_if_not_exists(toolbelt_paths.toolbelt_dir)

        if repo:
            repo.create_remote(name="origin", url=toolbelt_config.url)
        self.toolbelt.save()
        return 0

    def add(self, url: str, this_toolbelt: bool, fetch: bool) -> int:
        if this_toolbelt:
            return self._add_this_repo()

        toolbelt_config = ToolbeltConfig.from_url(url)
        self.toolbelt_paths.name = toolbelt_config.name

        # now we have the toolbelt name, we can set the path
        toolbelt_config.path = self.toolbelt_paths.toolbelt_install_dir.as_posix()
        self.toolbelt.add(toolbelt_config)
        self.toolbelt.save()

        if fetch:
            return self.fetch(toolbelt_config.name)
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
        toolbelt_paths = ToolbeltPaths(toolbelt_root=PYTOOLBELT_TOOLBELT_INSTALL_DIR)

        toolbelt_config = self.toolbelt.get(name)
        toolbelt_paths.name = toolbelt_config.name
        git_client = GitClient.clone_from_url(toolbelt_config.url, toolbelt_paths.toolbelt_install_dir)

        # main is the default branch, set master if old school
        if "master" in git_client.repo.branches:
            toolbelt_config.release_branch = "master"
            self.toolbelt.add(toolbelt_config)
            self.toolbelt.save()
        return 0
