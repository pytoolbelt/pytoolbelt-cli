from dataclasses import dataclass
from pathlib import Path

from pytoolbelt.cli.controllers.ptvenv_controller import PtVenvController
from pytoolbelt.cli.entrypoints.bases.base_parameters import BaseEntrypointParameters
from pytoolbelt.core.data_classes.pytoolbelt_config import (
    PytoolbeltConfig,
    pytoolbelt_config,
)
from pytoolbelt.core.data_classes.toolbelt_config import ToolbeltConfig


@dataclass
class PtVenvParameters(BaseEntrypointParameters):
    name: str
    toolbelt: str
    all: bool
    force: bool
    part: str
    from_config: bool


@pytoolbelt_config(provide_ptc=True)
def new(ptc: PytoolbeltConfig, toolbelt: ToolbeltConfig, params: PtVenvParameters) -> int:
    ptvenv = PtVenvController.for_creation(params.name, toolbelt)
    return ptvenv.create(ptc)


@pytoolbelt_config()
def install(toolbelt: ToolbeltConfig, params: PtVenvParameters) -> int:
    ptvenv = PtVenvController.for_build(params.name, toolbelt)
    return ptvenv.build(force=params.force, from_config=params.from_config)


def remove(params: PtVenvParameters) -> int:
    ptvenv = PtVenvController.for_deletion(params.name)
    return ptvenv.delete(params.all)


@pytoolbelt_config(provide_ptc=True)
def bump(ptc: PytoolbeltConfig, toolbelt: ToolbeltConfig, params: PtVenvParameters) -> int:
    ptvenv = PtVenvController.for_build(params.name, toolbelt)
    return ptvenv.bump(ptc, params.part)


@pytoolbelt_config(provide_ptc=True)
def release(ptc: PytoolbeltConfig, toolbelt: ToolbeltConfig, params: PtVenvParameters) -> int:
    ptvenv = PtVenvController.for_release(params.name, toolbelt)
    return ptvenv.release(ptc)


COMMON_FLAGS = {
    "--name": {
        "help": "Name of the ptvenv definition.",
        "required": True,
    },
    "--toolbelt": {
        "help": "Name of the toolbelt.",
        "required": False,
        "default": Path.cwd().name,
    },
}


ACTIONS = {
    "new": {
        "func": new,
        "help": "Create a new ptvenv definition file, or bump an existing one to a new version.",
    },
    "install": {
        "func": install,
        "help": "Install a pytoolbelt ptvenv from a ptvenv definition yml file.",
        "flags": {
            "--force": {
                "help": "Force rebuild of the ptvenv even if it already exists or has been changed.",
                "action": "store_true",
                "default": False,
            },
            "--from-config": {
                "help": "Build the ptvenv from the current pytoolbelt configuration.",
                "action": "store_true",
                "default": False,
            },
        },
    },
    "remove": {
        "func": remove,
        "help": "Remove a ptvenv definition from the local project.",
        "flags": {
            "--all": {
                "help": "Remove all versions of the ptvenv definition.",
                "action": "store_true",
                "default": False,
            },
        },
    },
    "bump": {
        "func": bump,
        "help": "Bump a ptvenv definition to a new version.",
        "flags": {
            "--part": {
                "help": "Part of the version to bump. (major, minor, patch, prerelease)",
                "required": False,
                "default": "config",
                "choices": ["major", "minor", "patch", "prerelease", "config"],
            },
        },
    },
    "release": {
        "func": release,
        "help": "Release a ptvenv definition to a remote git repository.",
    },
}
