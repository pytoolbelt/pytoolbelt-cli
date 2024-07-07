from dataclasses import dataclass
from pytoolbelt.cli.entrypoints.bases.base_parameters import BaseEntrypointParameters
from pytoolbelt.cli.controllers.toolbelt_controller import ToolbeltController


@dataclass
class ToolbeltParameters(BaseEntrypointParameters):
    url: str
    this_toolbelt: bool

    def __post_init__(self):
        if self.this_toolbelt and self.url:
            raise ValueError("Cannot provide both --url and --this-repo flags.")

        if not self.this_toolbelt and not self.url:
            raise ValueError("Must provide either --url or --this-repo flag.")


def add(params: ToolbeltParameters) -> int:
    controller = ToolbeltController()
    return controller.add(params.url, params.this_toolbelt)


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
            }
        },
    }
}
