from pytoolbelt.controllers.parameters import BaseControllerParameters
from pytoolbelt.core import project as p
from dataclasses import dataclass
from git import Repo
from pytoolbelt.environment.config import PYTOOLBELT_PROJECT_ROOT


@dataclass
class ProjectParameters(BaseControllerParameters):
    overwrite: bool


class ProjectContext:
    def __init__(self, params: ProjectParameters) -> None:
        self.params = params


def init(context: ProjectContext) -> int:
    paths = p.ProjectPaths()
    paths.create()
    templater = p.ProjectTemplater(paths)
    templater.template_new_project_files(context.params.overwrite)

    if not paths.git_dir.exists():
        Repo.init(PYTOOLBELT_PROJECT_ROOT)
    return 0


COMMON_FLAGS = {}

ACTIONS = {
    "init": {
        "func": init,
        "help": "Init a new pytoolbelt project repo.",
        "flags": {
            "--overwrite": {
                "help": "Overwrite existing files",
                "action": "store_true",
                "default": False,
            }
        }
    }
}
