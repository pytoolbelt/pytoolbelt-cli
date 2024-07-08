from dataclasses import dataclass

from pytoolbelt.cli.entrypoints.bases.base_parameters import BaseEntrypointParameters
from pytoolbelt.core.project import Tool


@dataclass
class ToolParameters(BaseEntrypointParameters):
    name: str
    repo_config: str
    dev_mode: bool


def new(params: ToolParameters) -> int:
    paths = Tool.from_cli(params.name, creation=True)
    paths.create()
    return 0


def install(params: ToolParameters) -> int:
    tool = Tool.from_cli(params.name, release=True)
    tool.install(dev_mode=params.dev_mode)
    return 0


def installed(params: ToolParameters) -> int:
    tool = Tool.from_cli("")
    tool.installed()
    return 0


def remove(params: ToolParameters) -> int:
    tool = Tool.from_cli(params.name)
    tool.remove()
    return 0


def release(params: ToolParameters) -> int:
    tool = Tool.from_cli(params.name, release=True)
    tool.release()
    return 0


def releases(params: ToolParameters) -> int:
    tool = Tool.from_cli(params.name, release=True)
    tool.releases()
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
    "releases": {
        "func": releases,
        "help": "List all releases",
    },
}
