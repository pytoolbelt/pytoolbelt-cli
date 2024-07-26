from dataclasses import dataclass
from pathlib import Path

from pytoolbelt.cli.controllers.toolbelt_controller import ToolbeltController
from pytoolbelt.cli.entrypoints.bases.base_parameters import BaseEntrypointParameters
from pytoolbelt.core.data_classes.pytoolbelt_config import pytoolbelt_config
from pytoolbelt.core.data_classes.toolbelt_config import ToolbeltConfig
from pytoolbelt.core.error_handling.exceptions import PytoolbeltError
from pytoolbelt.environment.config import get_logger


@dataclass
class ToolbeltParameters(BaseEntrypointParameters):
    url: str
    toolbelt: str
    this_toolbelt: bool
    fetch: bool

    def __post_init__(self):
        if self.action == "add":
            self._validate_on_add_action()

        if self.toolbelt and not self.toolbelt.endswith("-toolbelt"):
            raise PytoolbeltError("Toolbelt name must end with '-toolbelt'.")

    def _validate_on_add_action(self) -> None:
        if self.this_toolbelt and self.url:
            raise PytoolbeltError("Cannot provide both --url and --this-repo flags.")

        if not self.this_toolbelt and not self.url:
            raise PytoolbeltError("Must provide either --url or --this-repo flag.")


def new(params: ToolbeltParameters) -> int:
    controller = ToolbeltController()
    return controller.create(url=params.url)


def add(params: ToolbeltParameters) -> int:
    controller = ToolbeltController()
    return controller.add(params.url, params.this_toolbelt)


def remove(params: ToolbeltParameters) -> int:
    controller = ToolbeltController()
    return controller.remove(params.toolbelt)


def show(params: ToolbeltParameters) -> int:
    controller = ToolbeltController()
    return controller.show()


@pytoolbelt_config()
def fetch(toolbelt: ToolbeltConfig, params: ToolbeltParameters) -> int:
    controller = ToolbeltController()
    return controller.fetch(toolbelt=toolbelt)


COMMON_FLAGS = {}

ACTIONS = {
    "add": {
        "func": add,
        "help": "add a new toolbelt entry in the global config.",
        "flags": {
            "--url": {
                "help": "The url of the pytoolbelt repo to add to the global config.",
                "required": False,
            },
            "--this-toolbelt": {
                "help": "Add the origin remote config for this pytoolbelt repo to the global config.",
                "action": "store_true",
                "default": False,
            },
        },
    },
    "new": {
        "func": new,
        "help": "Create a new pytoolbelt.",
        "flags": {
            "--url": {
                "help": "The git url of the new project.",
                "required": False,
            },
        },
    },
    "remove": {
        "func": remove,
        "help": "Remove a toolbelt entry from the global config.",
        "flags": {
            "--toolbelt": {
                "help": "The name of the toolbelt to remove.",
                "required": True,
            }
        },
    },
    "show": {
        "func": show,
        "help": "Show all toolbelts in the global config.",
        "flags": {},
    },
    "fetch": {
        "func": fetch,
        "help": "Fetch the toolbelt from the global config.",
        "flags": {
            "--toolbelt": {
                "help": "The name of the toolbelt to fetch.",
                "required": False,
                "default": Path.cwd().name,
            }
        },
    },
}
