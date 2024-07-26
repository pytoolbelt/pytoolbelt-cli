from pathlib import Path

import giturlparse
from git import Repo, exc

from pytoolbelt.cli.views.toolbelt_views import ToolbeltConfigView
from pytoolbelt.core.data_classes.toolbelt_config import ToolbeltConfig, ToolbeltConfigs
from pytoolbelt.core.error_handling.exceptions import PytoolbeltError
from pytoolbelt.core.project.toolbelt_components import ToolbeltPaths, ToolbeltTemplater
from pytoolbelt.core.tools.git_client import GitClient
from pytoolbelt.environment.config import get_logger

logger = get_logger(__name__)


class ToolbeltController:
    def __init__(self) -> None:
        self.toolbelt_configs = ToolbeltConfigs.load()

    def _add_this_repo(self) -> int:
        repo = Repo(Path.cwd())

        toolbelt_paths = ToolbeltPaths(Path.cwd())
        toolbelt_paths.raise_if_not_exists()
        toolbelt_paths.raise_if_not_pytoolbelt_project()

        if not giturlparse.parse(repo.remotes.origin.url).valid:
            raise PytoolbeltError(f"Invalid git url: {repo.remotes.origin.url}")

        toolbelt_config = ToolbeltConfig.from_url(repo.remotes.origin.url)
        self.toolbelt_configs.add(toolbelt_config)
        self.toolbelt_configs.save()
        logger.info(f"Toolbelt {toolbelt_config.name} added to toolbelt.yml with url {toolbelt_config.url}.")
        return 0

    def create(self, url: str) -> int:

        toolbelt = ToolbeltConfig.from_url(url)
        logger.debug(f"Creating toolbelt {toolbelt.name} at {toolbelt.path}")

        toolbelt_paths = ToolbeltPaths(toolbelt_root=toolbelt.path)
        toolbelt_paths.raise_if_not_exists()
        toolbelt_paths.create()

        logger.debug(f"Creating toolbelt files at {toolbelt_paths.toolbelt_dir}")
        templater = ToolbeltTemplater(toolbelt_paths)
        templater.template_new_toolbelt_files()

        self.toolbelt_configs.add(toolbelt)
        logger.debug(f"Adding toolbelt {toolbelt.name} to config file")

        logger.debug(f"Initializing git repo at {toolbelt_paths.toolbelt_dir}")
        repo = GitClient.init_if_not_exists(toolbelt_paths.toolbelt_dir)

        if repo:
            logger.debug(f"Adding remote origin {toolbelt.url}")
            repo.create_remote(name="origin", url=toolbelt.url)

        logger.debug(f"Saving toolbelt config file")
        self.toolbelt_configs.save()

        logger.info(f"Toolbelt {toolbelt.name} created at {toolbelt.path}")
        return 0

    def add(self, url: str, this_toolbelt: bool) -> int:

        if this_toolbelt:
            logger.debug("Adding this repo as a toolbelt")
            return self._add_this_repo()

        toolbelt = ToolbeltConfig.from_url(url)
        self.toolbelt_configs.add(toolbelt)
        self.toolbelt_configs.save()
        logger.info(f"Toolbelt {toolbelt.name} added to toolbelt.yml config file with url {toolbelt.url}.")
        return 0

    def remove(self, toolbelt: str) -> int:
        try:
            _ = self.toolbelt_configs.repos.pop(toolbelt)
        except KeyError:
            raise PytoolbeltError(f"Toolbelt {toolbelt} not found in config file.")
        else:
            self.toolbelt_configs.save()
            logger.info(f"Toolbelt {toolbelt} removed from config file.")
            return 0

    def show(self) -> int:
        table = ToolbeltConfigView()
        table.add_configs(self.toolbelt_configs)
        table.print_table()
        return 0

    def fetch(self, toolbelt: ToolbeltConfig) -> int:
        try:
            git_client = GitClient.clone_from_url(toolbelt.url, toolbelt.path)
        except exc.GitCommandError as e:
            raise PytoolbeltError(f"Error fetching toolbelt: {e}")

        # main is the default branch, set master if old school
        if "master" in git_client.repo.branches:
            toolbelt.release_branch = "master"
            self.toolbelt_configs.add(toolbelt)
            self.toolbelt_configs.save()
        return 0
