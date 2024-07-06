from dataclasses import dataclass
from pytoolbelt.cli.entrypoints.bases.base_parameters import BaseEntrypointParameters
from pytoolbelt.cli.controllers.project_controller import Project


@dataclass
class ProjectParameters(BaseEntrypointParameters):
    overwrite: bool


def init(params: ProjectParameters) -> int:
    project = Project()
    project.create(overwrite=params.overwrite)
    return 0


COMMON_FLAGS = {}

ACTIONS = {
    "init": {
        "func": init,
        "help": "Init a new pytoolbelt project repo.",
        "flags": {
            "--overwrite": {
                "help": "Overwrite existing files if they already exist.",
                "action": "store_true",
                "default": False,
            }
        },
    }
}
