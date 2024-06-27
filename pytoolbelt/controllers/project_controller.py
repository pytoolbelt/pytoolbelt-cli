from pytoolbelt.controllers.bases.baseparameters import BaseControllerParameters
from pytoolbelt.controllers.bases.basecontext import BaseContext
from pytoolbelt.core import project
from dataclasses import dataclass
from pytoolbelt.core.git_commands import GitCommands
from pytoolbelt.environment.config import PYTOOLBELT_PROJECT_ROOT


@dataclass
class ProjectParameters(BaseControllerParameters):
    overwrite: bool


class ProjectContext(BaseContext[ProjectParameters]):
    def __init__(self, params: ProjectParameters) -> None:
        super().__init__(params=params)


def init(context: ProjectContext) -> int:

    paths = project.ProjectPaths()
    paths.create()

    templater = project.ProjectTemplater(paths)
    templater.template_new_project_files(context.params.overwrite)

    GitCommands.init_if_not_exists(PYTOOLBELT_PROJECT_ROOT)
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
