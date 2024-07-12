from dataclasses import dataclass

from pytoolbelt.cli.entrypoints.bases.base_parameters import BaseEntrypointParameters
from pytoolbelt.cli.controllers.tool_controller import ToolController


@dataclass
class ToolParameters(BaseEntrypointParameters):
    name: str
    dev_mode: bool


def new(params: ToolParameters) -> int:
    tool = ToolController.for_creation(params.name)
    return tool.create()


def remove(params: ToolParameters) -> int:
    tool = Tool.from_cli(params.name)
    tool.remove()
    return 0


def install(params: ToolParameters) -> int:
    tool = ToolController.for_installation(params.name)
    return tool.install(dev_mode=params.dev_mode)


def installed(params: ToolParameters) -> int:
    tool = Tool.from_cli("")
    tool.installed()
    return 0


def release(params: ToolParameters) -> int:
    tool = Tool.from_cli(params.name, release=True)
    tool.release()
    return 0


COMMON_FLAGS = {}

ACTIONS = {
    "new": {
        "func": new,
        "help": "Create a new tool",
        "flags": {"--name": {"help": "Name of the tool", "required": True}},
    },
    "install": {
        "func": install,
        "help": "Install the tool",
        "flags": {
            "--name": {
                "help": "Name of the tool",
                "required": True,
            },
            "--dev-mode": {
                "help": "Install in dev mode",
                "action": "store_true",
                "default": False,
            },
        },
    },
    "installed": {
        "func": installed,
        "help": "List installed tools",
        "flags": {
            "--name": {
                "help": "Name of the tool to list",
                "required": False,
                "default": "",
            }
        },
    },
    "remove": {
        "func": remove,
        "help": "Remove the tool",
        "flags": {
            "--name": {
                "help": "Name of the tool",
                "required": True,
            }
        },
    },
    "release": {
        "func": release,
        "help": "Release the tool",
        "flags": {
            "--name": {
                "help": "Name of the tool",
                "required": True,
            }
        },
    },
}
