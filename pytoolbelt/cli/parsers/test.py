from argparse import Namespace
from typing import Any
from pytoolbelt.cli.entrypoints import test_entrypoints
from pytoolbelt.core.error_handling.error_handler import handle_cli_errors
from pytoolbelt.core.tools import build_entrypoint_parsers


@handle_cli_errors
def entrypoint(cliargs: Namespace) -> int:
    params = test_entrypoints.TestParameters.from_cliargs(cliargs)
    action = test_entrypoints.ACTIONS[params.action]["func"]
    return action(params=params)


def configure_parser(subparser: Any) -> None:
    build_entrypoint_parsers(
        subparser=subparser,
        name="test",
        root_help="Interact with pytoolbelt tests",
        entrypoint=entrypoint,
        actions=test_entrypoints.ACTIONS,
        common_flags=test_entrypoints.COMMON_FLAGS,
    )
