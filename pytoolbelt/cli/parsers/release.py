from argparse import Namespace
from typing import Any

from pytoolbelt.cli.controllers.release_controller import (
    COMMON_FLAGS,
    ReleaseController,
    ReleaseParameters,
)
from pytoolbelt.core.error_handling.error_handler import handle_cli_errors
from pytoolbelt.core.tools import build_entrypoint_parsers


@handle_cli_errors
def entrypoint(cliargs: Namespace) -> int:
    params = ReleaseParameters.from_cliargs(cliargs)
    controller = ReleaseController()
    controller.release(params=params)
    return 0


def configure_parser(subparser: Any) -> None:
    build_entrypoint_parsers(
        subparser=subparser,
        name="release",
        root_help="Make releases for a pytoolbelt.",
        entrypoint=entrypoint,
        common_flags=COMMON_FLAGS,
    )
