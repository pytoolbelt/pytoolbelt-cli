from dataclasses import dataclass
from pathlib import Path

from pytoolbelt.cli.entrypoints.bases.base_parameters import BaseEntrypointParameters
from pytoolbelt.cli.views.releases_view import ReleasesTableView
from pytoolbelt.core.data_classes.component_metadata import ComponentMetadata
from pytoolbelt.core.data_classes.toolbelt_config import ToolbeltConfigs
from pytoolbelt.core.error_handling.exceptions import PytoolbeltError
from pytoolbelt.core.project.toolbelt_components import ToolbeltPaths
from pytoolbelt.core.tools.git_client import GitClient
from pytoolbelt.environment.config import get_logger

logger = get_logger(__name__)


@dataclass
class ReleasesParameters(BaseEntrypointParameters):
    toolbelt: str
    name: str
    ptvenv: bool
    tools: bool
    all: bool

    def __post_init__(self) -> None:

        if self.ptvenv and self.tools:
            raise PytoolbeltError("Cannot specify both --ptvenv and --tools")

        if not self.ptvenv and not self.tools:
            raise PytoolbeltError("Must specify either --ptvenv or --tools")


COMMON_FLAGS = {
    "--toolbelt": {"required": False, "help": "The help for toolbelt", "default": Path.cwd().name},
    "--ptvenv": {
        "required": False,
        "help": "The help for the ptvenv flag",
        "action": "store_true",
    },
    "--tools": {
        "required": False,
        "help": "The help for the tools flag.",
        "action": "store_true",
    },
    "--all": {
        "required": False,
        "help": "The help for the all flag",
        "action": "store_true",
    },
}


class ReleasesController:
    def __init__(self, toolbelt: str) -> None:
        self.toolbelt_configs = ToolbeltConfigs.load()
        self.toolbelt = self.toolbelt_configs.get(toolbelt)
        self.toolbelt_paths = ToolbeltPaths(self.toolbelt.path)

    def releases(self, ptvenv: bool, tools: bool, _all: bool) -> int:
        self.toolbelt_paths.raise_if_not_exists()
        git_client = GitClient.from_path(self.toolbelt.path, self.toolbelt)

        git_client.repo.remotes.origin.fetch()

        releases = []

        if ptvenv:
            releases = [(ComponentMetadata.from_release_tag(t.name), t) for t in git_client.ptvenv_releases()]

        if tools:
            releases = [(ComponentMetadata.from_release_tag(t.name), t) for t in git_client.tool_releases()]

        if not releases:
            logger.info(f"No releases found for toolbelt {self.toolbelt.name}")
            return 0

        # otherwise just do all the releases
        table = ReleasesTableView(toolbelt=self.toolbelt, ptvenv=ptvenv, tools=tools, _all=_all)
        for r, t in releases:
            table.add_row(r.name, r.version, str(t.commit.committed_datetime.date()), t.commit.hexsha)
        table.print_table()
