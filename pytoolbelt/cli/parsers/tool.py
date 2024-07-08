from argparse import Namespace
from typing import Any

from pytoolbelt.cli.entrypoints import tool_entrypoints
from pytoolbelt.core.error_handling.error_handler import handle_cli_errors
from pytoolbelt.core.tools import build_entrypoint_parsers


@handle_cli_errors
def entrypoint(cliargs: Namespace) -> int:
    params = tool_entrypoints.ToolParameters.from_cliargs(cliargs)
    action = tool_entrypoints.ACTIONS[params.action]["func"]
    return action(params=params)


def configure_parser(subparser: Any) -> None:
    build_entrypoint_parsers(
        subparser=subparser,
        name="tool",
        root_help="Interact with pytoolbelt tools",
        entrypoint=entrypoint,
        actions=tool_entrypoints.ACTIONS,
        common_flags=tool_entrypoints.COMMON_FLAGS,
    )
