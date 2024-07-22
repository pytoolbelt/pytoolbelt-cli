from dataclasses import dataclass

from pytoolbelt.cli.entrypoints.bases.base_parameters import BaseEntrypointParameters
from pytoolbelt.cli.views.installed_view import InstalledTableView
from pytoolbelt.core.data_classes.toolbelt_config import ToolbeltConfigs
from pytoolbelt.core.error_handling.exceptions import PytoolbeltError
from pytoolbelt.core.project.ptvenv_components import PtVenvPaths
from pytoolbelt.core.project.tool_components import ToolPaths
from pytoolbelt.core.project.toolbelt_components import ToolbeltPaths


@dataclass
class InstalledParameters(BaseEntrypointParameters):
    ptvenv: bool
    tools: bool

    def __post_init__(self) -> None:
        if self.ptvenv and self.tools:
            raise PytoolbeltError("Cannot specify both --ptvenv and --tools")

        if not self.ptvenv and not self.tools:
            raise PytoolbeltError("Must specify either --ptvenv or --tools")


COMMON_FLAGS = {
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
}


class InstalledController:
    def __init__(self) -> None:
        self.toolbelts = ToolbeltConfigs.load()
        self.toolbelt_paths = ToolbeltPaths()

    def installed(self, ptvenv: bool, tools: bool) -> int:
        table = InstalledTableView(ptvenv=ptvenv, tools=tools)

        if ptvenv:
            for installed_ptvenv in self.toolbelt_paths.iter_installed_ptvenvs():
                paths = PtVenvPaths(installed_ptvenv, self.toolbelt_paths)
                table.add_row(installed_ptvenv.name, installed_ptvenv.version, paths.install_dir.as_posix())

        if tools:
            for installed_tool in self.toolbelt_paths.iter_installed_tools():
                paths = ToolPaths(installed_tool, self.toolbelt_paths)
                table.add_row(installed_tool.name, installed_tool.version, paths.install_path.as_posix())

        table.print_table()
        return 0
