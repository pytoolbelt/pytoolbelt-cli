from pytoolbelt.controllers.bases.base_parameters import BaseControllerParameters
from pytoolbelt.controllers.bases.base_context import BaseContext
from pytoolbelt.core.project import Project
from dataclasses import dataclass


@dataclass
class ProjectParameters(BaseControllerParameters):
    overwrite: bool


class ProjectContext(BaseContext[ProjectParameters]):
    def __init__(self, params: ProjectParameters) -> None:
        super().__init__(params=params)


def init(ctx: ProjectContext) -> int:
    project = Project()
    project.create(overwrite=ctx.params.overwrite)
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
        }
    }
}
