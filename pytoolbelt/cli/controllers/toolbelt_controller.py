import giturlparse
from pathlib import Path
from git import Repo
from typing import Optional
from pytoolbelt.core.data_classes.toolbelt_config import ToolbeltConfigs, ToolbeltConfig
from pytoolbelt.core.project.project_components import ProjectPaths, ProjectTemplater
from pytoolbelt.core.tools.git_client import GitClient
from pytoolbelt.core.error_handling.exceptions import ToolbeltConfigNotFound
from pytoolbelt.views.toolbelt_views import ToolbeltConfigView


class ToolbeltController:

    def __init__(self, root_path: Optional[Path] = None, **kwargs) -> None:
        self._project_paths = kwargs.get("paths", ProjectPaths(project_root=root_path))
        self.templater = kwargs.get("templater", ProjectTemplater(self._project_paths))
        self._toolbelt = ToolbeltConfigs.load()

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
        self.templater.template_new_project_files()
        repo = GitClient.init_if_not_exists(self.project_paths.project_dir)
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
