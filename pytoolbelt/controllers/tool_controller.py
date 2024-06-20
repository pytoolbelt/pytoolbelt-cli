from pytoolbelt.controllers.parameters import ControllerParameters


class ToolControllerParameters(ControllerParameters):
    pass


class ToolContext:
    def __init__(self, params: ToolControllerParameters) -> None:
        self.params = params


def new(context: ToolContext) -> int:
    print("new")
    return 0


COMMON_FLAGS = {}

ACTIONS = {
    "new": {
        "func": new,
        "help": "Create a new tool",
    }
}
