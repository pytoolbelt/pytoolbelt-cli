from dataclasses import dataclass
from pathlib import Path

from pytoolbelt.cli.entrypoints.bases.base_parameters import BaseEntrypointParameters
from pytoolbelt.core.data_classes.pytoolbelt_config import (
    PytoolbeltConfig,
    pytoolbelt_config,
)
from pytoolbelt.core.data_classes.toolbelt_config import ToolbeltConfig
from pytoolbelt.cli.controllers.test_controller import TestController


@dataclass
class TestParameters(BaseEntrypointParameters):
    toolbelt: str


@pytoolbelt_config(provide_ptc=True)
def pull(ptc: PytoolbeltConfig, toolbelt: ToolbeltConfig, params: TestParameters) -> int:
    test_controller = TestController(ptc, toolbelt)
    test_controller.pull()
    return 0


@pytoolbelt_config(provide_ptc=True)
def run(ptc: PytoolbeltConfig, toolbelt: ToolbeltConfig, params: TestParameters) -> int:
    print(params)
    test_controller = TestController(ptc, toolbelt)
    test_controller.run()
    return 0


@pytoolbelt_config(provide_ptc=True)
def render(ptc: PytoolbeltConfig, toolbelt: ToolbeltConfig, params: TestParameters) -> int:
    test_controller = TestController(ptc, toolbelt)
    test_controller.render()
    return 0


COMMON_FLAGS = {
    "--toolbelt": {
        "help": "Name of the toolbelt.",
        "required": False,
        "default": Path.cwd().name,
    },
}


ACTIONS = {
    "pull": {
        "func": pull,
        "help": "Pull the test docker image for the toolbelt.",
    },
    "run": {
        "func": run,
        "help": "Run the tests for a given toolbelt.",
    },
    "render": {
        "func": render,
        "help": "Render noxfile.py for a given toolbelt.",
    },
}
