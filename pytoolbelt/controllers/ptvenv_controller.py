from dataclasses import dataclass

from pytoolbelt.controllers.bases.base_parameters import BaseControllerParameters
from pytoolbelt.core.project import PtVenv


@dataclass
class VenvDefControllerParameters(BaseControllerParameters):
    name: str
    repo_config: str
    all: bool
    force: bool
    part: str


class VenvDefContext:
    def __init__(self, params: VenvDefControllerParameters) -> None:
        self.params = params


def new(context: VenvDefContext) -> int:
    ptvenv = PtVenv.from_cli(context.params.name, creation=True)
    ptvenv.create()
    return 0


def build(context: VenvDefContext) -> int:
    # TODO: review if the repo config here is really needed. I think it should be removed from GitCommands.
    ptvenv = PtVenv.from_cli(context.params.name, build=True)
    ptvenv.build(context.params.force, context.params.repo_config)
    return 0


def remove(context: VenvDefContext) -> int:
    ptvenv = PtVenv.from_cli(context.params.name, deletion=True)
    ptvenv.delete(context.params.all)
    return 0


def bump(context: VenvDefContext) -> int:
    ptvenv = PtVenv.from_cli(context.params.name, build=True)
    ptvenv.bump(context.params.part)
    return 0


def release(context: VenvDefContext) -> int:
    ptvenv = PtVenv.from_cli(context.params.name, build=True)
    ptvenv.release()
    return 0


def releases(context: VenvDefContext) -> int:
    ptvenv = PtVenv.from_cli(context.params.name)
    ptvenv.releases(context.params.repo_config)
    return 0


def installed(context: VenvDefContext) -> int:
    ptvenv = PtVenv.from_cli(context.params.name)
    ptvenv.installed()
    return 0


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
                "default": "patch",
                "choices": ["major", "minor", "patch", "prerelease"],
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
    "releases": {
        "func": releases,
        "help": "List all ptvenv releases in the local git repository.",
        "flags": {
            "--name": {
                "help": "Name of the ptvenv definition to list releases for.",
                "default": "",
            },
            "--repo-config": {
                "help": "Name of the repo config to list the releases for.",
                "required": False,
                "default": "default",
            },
        },
    },
    "installed": {
        "func": installed,
        "help": "List all installed versions of a ptvenv definition.",
        "flags": {
            "--name": {
                "help": "Name of the ptvenv definition to list installed versions for.",
                "required": False,
                "default": "",
            }
        },
    },
}
