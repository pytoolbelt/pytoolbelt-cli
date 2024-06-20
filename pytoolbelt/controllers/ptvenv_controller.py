from dataclasses import dataclass
from pytoolbelt.controllers.parameters import ControllerParameters
from pytoolbelt.controllers.arg_validation import ValidateName
from pytoolbelt.core import ptvenv as vd


@dataclass
class VenvDefControllerParameters(ControllerParameters):
    bump: str


class VenvDefContext:
    def __init__(self, params: VenvDefControllerParameters) -> None:
        self.params = params


def debug(context: VenvDefContext) -> int:
    paths = vd.VenvDefPaths(name=context.params.name)
    paths.set_highest_version()
    paths.raise_if_venvdef_not_found()

    venvdef = paths.get_venvdef()
    venvdef.generate_hash()
    print(venvdef.ptvenv_hash)

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
    },
    "build": {
        "func": build,
        "help": "Build a pytoolbelt venv from a venvdef file",
        "flags": {
            "--bump": {
                "help": "Version of the venvdef",
                "required": False,
                "default": "patch",
                "choices": ["major", "minor", "patch", "prerelease"],
            },

        }
    },
    "debug": {
        "func": debug,
        "help": "Debug a venvdef file",
    },
}
