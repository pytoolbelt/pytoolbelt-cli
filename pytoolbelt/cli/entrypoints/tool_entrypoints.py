from dataclasses import dataclass
from pathlib import Path

from pytoolbelt.cli.controllers.tool_controller import ToolController
from pytoolbelt.cli.entrypoints.bases.base_parameters import BaseEntrypointParameters
from pytoolbelt.core.data_classes.pytoolbelt_config import (
    PytoolbeltConfig,
    pytoolbelt_config,
)
from pytoolbelt.core.data_classes.toolbelt_config import ToolbeltConfig


@dataclass
class ToolParameters(BaseEntrypointParameters):
    toolbelt: str
    part: str
    name: str
    dev_mode: bool
    from_config: bool


@pytoolbelt_config()
def new(toolbelt: ToolbeltConfig, params: ToolParameters) -> int:
    tool = ToolController.for_creation(params.name, toolbelt)
    return tool.create()


@pytoolbelt_config()
def remove(toolbelt: ToolbeltConfig, params: ToolParameters) -> int:
    tool = ToolController.for_deletion(params.name, toolbelt)
    return tool.remove()


@pytoolbelt_config()
def install(toolbelt: ToolbeltConfig, params: ToolParameters) -> int:
    tool = ToolController.for_installation(params.name, toolbelt)
    return tool.install(dev_mode=params.dev_mode, from_config=params.from_config)


@pytoolbelt_config(provide_ptc=True)
def bump(ptc: PytoolbeltConfig, toolbelt: ToolbeltConfig, params: ToolParameters) -> int:
    tool = ToolController.for_release(params.name, toolbelt)
    return tool.bump(ptc, params.part)


@pytoolbelt_config(provide_ptc=True)
def release(ptc: PytoolbeltConfig, toolbelt: ToolbeltConfig, params: ToolParameters) -> int:
    tool = ToolController.for_release(params.name, toolbelt)
    return tool.release(ptc)


COMMON_FLAGS = {
    "--name": {
        "help": "Name of the tool",
        "required": True,
    },
    "--toolbelt": {
        "help": "The name of the toolbelt to target.",
        "required": False,
        "default": Path.cwd().name,
    },
}


ACTIONS = {
    "new": {
        "func": new,
        "help": "Create a new tool in the toolbelt",
    },
    "install": {
        "func": install,
        "help": "Install the tool",
        "flags": {
            "--dev-mode": {
                "help": "Install the tool in development mode",
                "action": "store_true",
                "default": False,
            },
            "--from-config": {
                "help": "Install from the tool config, regardless of version",
                "action": "store_true",
                "default": False,
            },
        },
    },
    "bump": {
        "func": bump,
        "help": "Bump the tool semantic version.",
        "flags": {
            "--part": {
                "help": "Part of the version to bump",
                "required": False,
                "choices": ["major", "minor", "patch", "prerelease", "config"],
                "default": "config",
            },
        },
    },
    "remove": {
        "func": remove,
        "help": "Remove an installed tool",
    },
    "release": {
        "func": release,
        "help": "Release the tool",
    },
}
