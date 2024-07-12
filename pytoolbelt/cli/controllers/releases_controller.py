from dataclasses import dataclass
from pytoolbelt.core.data_classes.toolbelt_config import ToolbeltConfigs
from pytoolbelt.cli.entrypoints.bases.base_parameters import BaseEntrypointParameters
from pytoolbelt.cli.views.releases_view import ReleasesTableView
from pytoolbelt.core.project.toolbelt_components import ToolbeltPaths
from pytoolbelt.core.tools.git_client import GitClient
from pytoolbelt.core.data_classes.component_metadata import ComponentMetadata


@dataclass
class ReleasesParameters(BaseEntrypointParameters):
    toolbelt: str
    name: str
    ptvenv: bool
    tools: bool
    all: bool

    def __post_init__(self) -> None:

        if self.ptvenv and self.tools:
            raise ValueError("Cannot specify both --ptvenv and --tools")


COMMON_FLAGS = {
    "--toolbelt": {
        "required": True,
        "help": "The help for toolbelt"
    },
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
    }
}

class ReleasesController:

    def __init__(self) -> None:
        self.toolbelts = ToolbeltConfigs.load()
        self.toolbelt_paths = ToolbeltPaths()

    def releases(self, name: str, ptvenv: bool, tools: bool, _all: bool) -> None:
        toolbelt = self.toolbelts.get(name)
        self.toolbelt_paths.name = name
        git_client = GitClient.from_path(self.toolbelt_paths.toolbelt_install_dir, toolbelt)

        git_client.repo.remotes.origin.fetch()

        releases = []

        if ptvenv:
            releases = [(ComponentMetadata.from_release_tag(t.name), t) for t in git_client.ptvenv_releases()]

        if tools:
            releases = [(ComponentMetadata.from_release_tag(t.name), t) for t in git_client.tool_releases()]

        if not releases:
            print("No releases found for this toolbelt.")
            return 0

        # otherwise just do all the releases
        table = ReleasesTableView(toolbelt=toolbelt, ptvenv=ptvenv, tools=tools, _all=_all)
        for r, t in releases:
            table.add_row(r.name, r.version, str(t.commit.committed_datetime.date()), t.commit.hexsha)
        table.print_table()
