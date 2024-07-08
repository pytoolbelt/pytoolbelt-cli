from argparse import Namespace
from typing import Any

from pytoolbelt.cli.entrypoints import toolbelt_entrypoints
from pytoolbelt.core.error_handling.error_handler import handle_cli_errors
from pytoolbelt.core.tools import build_entrypoint_parsers


@handle_cli_errors
def entrypoint(cliargs: Namespace) -> int:
    params = toolbelt_entrypoints.ToolbeltParameters.from_cliargs(cliargs)
    action = toolbelt_entrypoints.ACTIONS[params.action]["func"]
    return action(params=params)


def configure_parser(subparser: Any) -> None:
    build_entrypoint_parsers(
        subparser=subparser,
        name="toolbelt",
        root_help="Interact with the pytoolbelt toolbelt config.",
        entrypoint=entrypoint,
        actions=toolbelt_entrypoints.ACTIONS,
        common_flags=toolbelt_entrypoints.COMMON_FLAGS,
    )
