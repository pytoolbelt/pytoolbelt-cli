from dataclasses import dataclass
from pytoolbelt.cli.entrypoints.bases.base_parameters import BaseEntrypointParameters
from pytoolbelt.cli.controllers.toolbelt_controller import ToolbeltController


@dataclass
class ToolbeltParameters(BaseEntrypointParameters):
    url: str
    name: str
    owner: str
    this_toolbelt: bool

    def __post_init__(self):
        if self.action == "add":
            self._validate_on_add_action()

        if self.action == "new":
            self._validate_on_new_action()

        if self.name and not self.name.endswith("-toolbelt"):
            raise ValueError("Toolbelt name must end with '-toolbelt'.")

    def _validate_on_add_action(self) -> None:
        if self.this_toolbelt and self.url:
            raise ValueError("Cannot provide both --url and --this-repo flags.")

        if not self.this_toolbelt and not self.url:
            raise ValueError("Must provide either --url or --this-repo flag.")

    def _validate_on_new_action(self) -> None:
        if (self.name or self.owner) and self.url:
            raise ValueError("Cannot provide both --url and --name/--owner flags.")


def new(params: ToolbeltParameters) -> int:
    controller = ToolbeltController()
    return controller.create(url=params.url, name=params.name, owner=params.owner)


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
    },
    "new": {
        "func": new,
        "help": "Create a new pytoolbelt.",
        "flags": {
            "--name": {
                "help": "The name of the new project. (git repo name)",
                "required": False,
            },
            "--owner": {
                "help": "The owner of the new project. (git repo owner)",
                "required": False,
            },
            "--url": {
                "help": "The git url of the new project.",
                "required": False,
            }
        },
    }
}
