import giturlparse
from pathlib import Path
from git import Repo, exc
from pytoolbelt.cli.views.toolbelt_views import ToolbeltConfigView
from pytoolbelt.core.data_classes.toolbelt_config import ToolbeltConfig, ToolbeltConfigs
from pytoolbelt.core.error_handling.exceptions import PytoolbeltError
from pytoolbelt.core.project.toolbelt_components import ToolbeltPaths, ToolbeltTemplater
from pytoolbelt.core.tools.git_client import GitClient


class ToolbeltController:
    def __init__(self) -> None:
        self.toolbelt_configs = ToolbeltConfigs.load()

    def _add_this_repo(self) -> int:
        repo = Repo(Path.cwd())

        toolbelt_paths = ToolbeltPaths(Path.cwd())
        toolbelt_paths.raise_if_not_exists()
        toolbelt_paths.raise_if_not_pytoolbelt_project(repo)

        if not giturlparse.parse(repo.remotes.origin.url).valid:
            raise PytoolbeltError(f"Invalid git url: {repo.remotes.origin.url}")

        toolbelt_config = ToolbeltConfig.from_url(repo.remotes.origin.url)
        self.toolbelt_configs.add(toolbelt_config)
        self.toolbelt_configs.save()
        return 0

    def create(self, url: str) -> int:

        toolbelt = ToolbeltConfig.from_url(url)

        toolbelt_paths = ToolbeltPaths(toolbelt_root=toolbelt.path)
        toolbelt_paths.raise_if_not_exists()
        toolbelt_paths.create()

        templater = ToolbeltTemplater(toolbelt_paths)
        templater.template_new_toolbelt_files()

        self.toolbelt_configs.add(toolbelt)

        repo = GitClient.init_if_not_exists(toolbelt_paths.toolbelt_dir)

        if repo:
            repo.create_remote(name="origin", url=toolbelt.url)
        self.toolbelt_configs.save()
        return 0

    def add(self, url: str, this_toolbelt: bool) -> int:

        if this_toolbelt:
            return self._add_this_repo()

        toolbelt = ToolbeltConfig.from_url(url)
        self.toolbelt_configs.add(toolbelt)
        self.toolbelt_configs.save()
        return 0

    def remove(self, name: str) -> int:
        try:
            _ = self.toolbelt_configs.repos.pop(name)
        except KeyError:
            raise PytoolbeltError(f"Toolbelt {name} not found in config file.")
        else:
            self.toolbelt_configs.save()
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
