from dataclasses import dataclass
from pytoolbelt.controllers.parameters import ControllerParameters
from pytoolbelt.controllers.arg_validation import ValidateName
from pytoolbelt.core import ptvenv as vd
from pytoolbelt.core.project import ProjectPaths


@dataclass
class VenvDefControllerParameters(ControllerParameters):
    bump: str
    repo_config: str


class VenvDefContext:
    def __init__(self, params: VenvDefControllerParameters) -> None:
        self.params = params


def debug(context: VenvDefContext) -> int:
    paths = vd.VenvDefPaths(name=context.params.name)
    paths.set_highest_version()
    paths.raise_if_venvdef_not_found()

    project_paths = ProjectPaths()
    config = project_paths.get_pytoolbelt_config()
    repo_config = config.get_repo_config(context.params.repo_config)
    print(repo_config)
    venvdef = paths.get_venvdef()
    venvdef.generate_hash()

    return 0


def build(context: VenvDefContext) -> int:
    paths = vd.VenvDefPaths(name=context.params.name)
    paths.set_highest_version()
    paths.raise_if_venvdef_not_found()

    venv_builder = vd.VenvBuilder(paths)
    venv_builder.build()
    return 0


def new(context: VenvDefContext) -> int:
    paths = vd.VenvDefPaths(name=context.params.name)
    paths.create_new_directories()
    paths.set_highest_version()
    paths.version = paths.version.next_version(context.params.bump)
    templater = vd.VenvDefTemplater(paths)
    templater.template_new_venvdef_file()
    return 0


COMMON_FLAGS = {
    "--name": {
        "help": "Name of the venvdef",
        "required": True,
        "action": ValidateName,
    }
}

ACTIONS = {
    "new": {
        "func": new,
        "help": "Create a new venvdef",
        "flags": {
            "--bump": {
                "help": "Version of the venvdef",
                "required": False,
                "default": "patch",
                "choices": ["major", "minor", "patch", "prerelease"],
            },
    },
    "build": {
        "func": build,
        "help": "Build a pytoolbelt venv from a venvdef file",


        }
    },
    "debug": {
        "func": debug,
        "help": "Debug a venvdef file",
        "flags": {
            "--repo-config": {
                "help": "Repo name",
                "default": "default",
            }
        }
    },
}
