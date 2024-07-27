from dataclasses import dataclass
from pathlib import Path

from pytoolbelt.core.tools.formatting import RuffFormatter, RuffInputSorter
from pytoolbelt.cli.entrypoints.bases.base_parameters import BaseEntrypointParameters
from pytoolbelt.core.data_classes.toolbelt_config import ToolbeltConfig
from pytoolbelt.core.data_classes.pytoolbelt_config import pytoolbelt_config
from pytoolbelt.environment.config import get_logger

logger = get_logger(__name__)


@dataclass
class FormatParameters(BaseEntrypointParameters):
    toolbelt: str


COMMON_FLAGS = {
    "--toolbelt": {
        "required": False,
        "help": "The help for toolbelt",
        "default": Path.cwd().name,
    },
}


class FormatController:

    @pytoolbelt_config()
    def format(self, params: FormatParameters, toolbelt: ToolbeltConfig) -> None:
        with RuffFormatter(toolbelt) as formatter:
            formatter.run()

        with RuffInputSorter(toolbelt) as sorter:
            sorter.run()
