from dataclasses import dataclass

from pytoolbelt.cli.entrypoints.bases.base_parameters import BaseEntrypointParameters
from pytoolbelt.cli.controllers.ptvenv_controller import PtVenv
from pytoolbelt.core.data_classes.pytoolbelt_config import pytoolbelt_config, PytoolbeltConfig


@dataclass
class PtVenvParameters(BaseEntrypointParameters):
    name: str
    repo: str
    all: bool
    force: bool
    part: str
    build: bool
    keep: bool


@pytoolbelt_config
def new(ptc: PytoolbeltConfig, params: PtVenvParameters) -> int:
    ptvenv = PtVenv.from_cli(params.name, creation=True)
    return ptvenv.create(ptc)


def build(params: PtVenvParameters) -> int:
    ptvenv = PtVenv.from_cli(params.name, build=True)
    return ptvenv.build(params.force)


def remove(params: PtVenvParameters) -> int:
    ptvenv = PtVenv.from_cli(params.name, deletion=True)
    return ptvenv.delete(params.all)


@pytoolbelt_config
def bump(ptc: PytoolbeltConfig, params: PtVenvParameters) -> int:
    ptvenv = PtVenv.from_cli(params.name, build=True)
    if params.part == "config":
        return ptvenv.bump(ptc.bump)
    return ptvenv.bump(params.part)


@pytoolbelt_config
def release(ptc: PytoolbeltConfig, params: PtVenvParameters) -> int:
    ptvenv = PtVenv.from_cli(params.name, build=True)
    return ptvenv.release(ptc)


def releases(params: PtVenvParameters) -> int:
    ptvenv = PtVenv.from_cli(params.name)
    return ptvenv.releases(params.repo)


def installed(params: PtVenvParameters) -> int:
    ptvenv = PtVenv.from_cli(params.name)
    return ptvenv.installed()


def fetch(params: PtVenvParameters) -> int:
    # TODO: This likely goes away....
    ptvenv = PtVenv.from_cli(params.name)
    ptvenv.fetch(
        repo_config_name=params.repo,
        build=params.build,
        force=params.force,
        keep=params.keep,

    )
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
    "fetch": {
        "func": fetch,
        "help": "Fetch the ptvenv definition from the remote git repository.",
        "flags": {
            "--name": {
                "help": "Name of the ptvenv definition to fetch.",
                "required": True,
            },
            "--repo-config": {
                "help": "Name of the repo config to fetch the ptvenv definition from.",
                "required": True
            },
            "--build": {
                "help": "Build the ptvenv after fetching.",
                "action": "store_true",
                "default": False,
            },
            "--force": {
                "help": "Force build after fetching.",
                "action": "store_true",
                "default": False,
            },
            "--keep": {
                "help": "Keep the fetched ptvenv definition in the local project.",
                "action": "store_true",
                "default": False,
            }
        },
    },
}
