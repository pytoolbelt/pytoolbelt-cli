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


@pytoolbelt_config
def new(ptc: PytoolbeltConfig, toolbelt: ToolbeltConfig, params: ToolParameters) -> int:
    tool = ToolController.for_creation(params.name, root_path=toolbelt.path)
    return tool.create()


def remove(params: ToolParameters) -> int:
    tool = ToolController.for_deletion(params.name)
    return tool.remove()


@pytoolbelt_config
def install(ptc: PytoolbeltConfig, toolbelt: ToolbeltConfig, params: ToolParameters) -> int:
    tool = ToolController.for_installation(params.name, root_path=toolbelt.path)
    return tool.install(
        dev_mode=params.dev_mode,
        path=toolbelt.path,
        toolbelt=toolbelt.name,
        from_config=params.from_config,
    )


@pytoolbelt_config
def bump(ptc: PytoolbeltConfig, toolbelt: PytoolbeltConfig, params: ToolParameters) -> int:
    tool = ToolController.for_release(params.name, root_path=toolbelt.path)
    if params.part == "config":
        return tool.bump(ptc.bump)
    return tool.bump(params.part)


@pytoolbelt_config
def release(ptc: PytoolbeltConfig, toolbelt: ToolbeltConfig, params: ToolParameters) -> int:
    tool = ToolController.for_release(params.name, root_path=toolbelt.path)
    tool.release(ptc)
    return 0


COMMON_FLAGS = {}

ACTIONS = {
    "new": {
        "func": new,
        "help": "Create a new tool",
        "flags": {
            "--name": {"help": "Name of the tool", "required": True},
            "--toolbelt": {
                "help": "The help for toolbelt",
                "required": False,
                "default": Path.cwd().name,
            },
        },
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
            "--toolbelt": {
                "help": "The help for toolbelt",
                "required": False,
                "default": Path.cwd().name,
            },
            "--from-config": {
                "help": "Install from the toolbelt config",
                "action": "store_true",
                "default": False,
            },
        },
    },
    "bump": {
        "func": bump,
        "help": "Bump the tool",
        "flags": {
            "--name": {
                "help": "Name of the tool",
                "required": True,
            },
            "--part": {
                "help": "Part of the version to bump",
                "required": False,
                "choices": ["major", "minor", "patch", "prerelease", "config"],
                "default": "config",
            },
            "--toolbelt": {
                "help": "The help for toolbelt",
                "required": False,
                "default": Path.cwd().name,
            },
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
            },
            "--toolbelt": {
                "help": "The help for toolbelt",
                "required": False,
                "default": Path.cwd().name,
            },
        },
    },
}
