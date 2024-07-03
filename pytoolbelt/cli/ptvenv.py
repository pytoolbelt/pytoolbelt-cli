from argparse import Namespace
from typing import Any

from pytoolbelt.controllers import ptvenv_controller as c
from pytoolbelt.core.build_entrypoint_parser import build_entrypoint_parsers
from pytoolbelt.core.error_handler import handle_cli_errors


@handle_cli_errors
def entrypoint(cliargs: Namespace) -> int:
    params = c.VenvDefControllerParameters.from_cliargs(cliargs)
    context = c.VenvDefContext(params)
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
