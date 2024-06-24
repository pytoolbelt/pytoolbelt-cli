from pytoolbelt.controllers.parameters import ControllerParameters
from pytoolbelt.controllers.arg_validation import ValidateName
from pytoolbelt.core import tool
from pytoolbelt.core.ptvenv import PtVenvPaths
from semver import Version


class ToolControllerParameters(ControllerParameters):
    pass


class ToolContext:
    def __init__(self, params: ToolControllerParameters) -> None:
        self.params = params


def new(context: ToolContext) -> int:
    tp = tool.ToolPaths(context.params.name)
    tp.create()

    templater = tool.ToolTemplater(tp)
    templater.template_new_tool_files()
    return 0


def install(context: ToolContext) -> int:
    tp = tool.ToolPaths(context.params.name)
    tool_config = tp.get_tool_config()
    ptvenv_paths = PtVenvPaths(
        name=tool_config.ptvenv.name,
        version=Version.parse(tool_config.ptvenv.version)
    )

    tool_installer = tool.ToolInstaller(tp)
    tool_installer.install(ptvenv_paths.executable_path.as_posix())

    return 0


COMMON_FLAGS = {}

ACTIONS = {
    "new": {
        "func": new,
        "help": "Create a new tool",
        "flags": {
            "--name": {
                "help": "Name of the tool",
                "required": True,
                "action": ValidateName,
            }
        }
    },
    "install": {
        "func": install,
        "help": "Install the tool",
        "flags": {
            "--name": {
                "help": "Name of the tool",
                "required": True,
                "action": ValidateName,
            }
        }
    }
}
