from argparse import Namespace
from typing import Any

from pytoolbelt.cli.entrypoints import ptvenv_entrypoints
from pytoolbelt.core.error_handling.error_handler import handle_cli_errors
from pytoolbelt.core.tools import build_entrypoint_parsers


@handle_cli_errors
def entrypoint(cliargs: Namespace) -> int:
    params = ptvenv_entrypoints.PtVenvParameters.from_cliargs(cliargs)
    action = ptvenv_entrypoints.ACTIONS[params.action]["func"]
    return action(params=params)


def configure_parser(subparser: Any) -> None:
    build_entrypoint_parsers(
        subparser=subparser,
        name="ptvenv",
        root_help="Interact with pytoolbelt venv",
        entrypoint=entrypoint,
        actions=ptvenv_entrypoints.ACTIONS,
        common_flags=ptvenv_entrypoints.COMMON_FLAGS,
    )
