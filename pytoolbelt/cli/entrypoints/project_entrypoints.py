from dataclasses import dataclass
from pytoolbelt.cli.entrypoints.bases.base_parameters import BaseControllerParameters
from pytoolbelt.cli.controllers.project_controller import Project
from pytoolbelt.core.data_classes.pytoolbelt_config import pytoolbelt_config, PytoolbeltConfig


@dataclass
class ProjectParameters(BaseControllerParameters):
    overwrite: bool


@pytoolbelt_config
def init(ptc: PytoolbeltConfig, params: ProjectParameters) -> int:
    print(ptc)
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
