from argparse import Namespace
from typing import Any

from pytoolbelt.controllers import tool_controller as tc
from pytoolbelt.core.build_entrypoint_parser import build_entrypoint_parsers
from pytoolbelt.core.error_handler import handle_cli_errors


@handle_cli_errors
def entrypoint(cliargs: Namespace) -> int:
    params = tc.ToolControllerParameters.from_cliargs(cliargs)
    context = tc.ToolContext(params)
    action = tc.ACTIONS[params.action]["func"]
    return action(context)


def configure_parser(subparser: Any) -> None:
    build_entrypoint_parsers(
        subparser=subparser,
        name="tool",
        root_help="Interact with pytoolbelt tools",
        entrypoint=entrypoint,
        actions=tc.ACTIONS,
        common_flags=tc.COMMON_FLAGS,
    )
