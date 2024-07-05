from dataclasses import dataclass

from pytoolbelt.controllers.bases.base_parameters import BaseControllerParameters
from pytoolbelt.core.project import Tool


@dataclass
class ToolControllerParameters(BaseControllerParameters):
    name: str
    repo_config: str
    dev_mode: bool


class ToolContext:
    def __init__(self, params: ToolControllerParameters) -> None:
        self.params = params


def new(context: ToolContext) -> int:
    paths = Tool.from_cli(context.params.name, creation=True)
    paths.create()
    return 0


def install(context: ToolContext) -> int:
    tool = Tool.from_cli(context.params.name, release=True)
    tool.install(repo_config="default", dev_mode=context.params.dev_mode)
    return 0


def installed(context: ToolContext) -> int:
    tool = Tool.from_cli("")
    tool.installed()
    return 0


def remove(context: ToolContext) -> int:
    tool = Tool.from_cli(context.params.name)
    tool.remove()
    return 0


def release(context: ToolContext) -> int:
    tool = Tool.from_cli(context.params.name, release=True)
    tool.release()
    return 0


def fetch(context: ToolContext) -> int:
    tool = Tool.from_cli(context.params.name, release=True)
    tool.fetch()
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
            }
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
        }
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
