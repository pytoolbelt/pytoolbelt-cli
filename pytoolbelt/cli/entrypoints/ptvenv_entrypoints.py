from dataclasses import dataclass
from pytoolbelt.cli.entrypoints.bases.base_parameters import BaseEntrypointParameters
from pytoolbelt.cli.controllers.ptvenv_controller import PtVenvController
from pytoolbelt.core.data_classes.pytoolbelt_config import pytoolbelt_config, PytoolbeltConfig


@dataclass
class PtVenvParameters(BaseEntrypointParameters):
    name: str
    all: bool
    force: bool
    part: str


@pytoolbelt_config
def new(ptc: PytoolbeltConfig, params: PtVenvParameters) -> int:
    ptvenv = PtVenvController.for_creation(params.name)
    return ptvenv.create(ptc)


def build(params: PtVenvParameters) -> int:
    ptvenv = PtVenvController.for_build_and_release(params.name)
    return ptvenv.build(params.force)


def remove(params: PtVenvParameters) -> int:
    ptvenv = PtVenvController.for_deletion(params.name)
    return ptvenv.delete(params.all)


@pytoolbelt_config
def bump(ptc: PytoolbeltConfig, params: PtVenvParameters) -> int:
    ptvenv = PtVenvController.for_build_and_release(params.name)
    if params.part == "config":
        return ptvenv.bump(ptc.bump)
    return ptvenv.bump(params.part)


@pytoolbelt_config
def release(ptc: PytoolbeltConfig, params: PtVenvParameters) -> int:
    ptvenv = PtVenvController.for_build_and_release(params.name)
    return ptvenv.release(ptc)


COMMON_FLAGS = {}

ACTIONS = {
    "new": {
        "func": new,
        "help": "Create a new ptvenv definition file, or bump an existing one to a new version.",
        "flags": {
            "--name": {
                "help": "Name of the ptvenv definition to create",
                "required": True,
            }
        },
    },
    "build": {
        "func": build,
        "help": "Build a pytoolbelt ptvenv from a ptvenv definition yml file.",
        "flags": {
            "--name": {
                "help": "Name of the ptvenv to build.",
                "required": True,
            },
            "--force": {
                "help": "Force rebuild of the ptvenv even if it already exists or has been changed.",
                "action": "store_true",
                "default": False,
            },
        },
    },
    "remove": {
        "func": remove,
        "help": "Remove a ptvenv definition from the local project.",
        "flags": {
            "--name": {
                "help": "Name of the ptvenv to remove. If no version provided, the most recent version will be removed.",
                "required": True,
            },
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
            "--name": {
                "help": "Name of the ptvenv definition to bump.",
                "required": True,
            },
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
        "flags": {
            "--name": {
                "help": "Name of the ptvenv definition to release.",
                "required": True,
            },
        },
    },
}
