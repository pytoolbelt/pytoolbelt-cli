from argparse import Namespace
from typing import Any

from pytoolbelt.cli.entrypoints import ptvenv_controller as c
from pytoolbelt.core.tools import build_entrypoint_parsers
from pytoolbelt.core.error_handling.error_handler import handle_cli_errors


@handle_cli_errors
def entrypoint(cliargs: Namespace) -> int:
    params = c.PtVenvControllerParameters.from_cliargs(cliargs)
    context = c.PtVenvContext(params)
    action = c.ACTIONS[params.action]["func"]
    return action(context)


def configure_parser(subparser: Any) -> None:
    build_entrypoint_parsers(
        subparser=subparser,
        name="ptvenv",
        root_help="Interact with pytoolbelt venv",
        entrypoint=entrypoint,
        actions=c.ACTIONS,
        common_flags=c.COMMON_FLAGS,
    )
