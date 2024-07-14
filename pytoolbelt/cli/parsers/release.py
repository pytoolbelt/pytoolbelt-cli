from argparse import Namespace
from typing import Any
from pytoolbelt.core.error_handling.error_handler import handle_cli_errors
from pytoolbelt.cli.controllers.release_controller import ReleaseController
from pytoolbelt.core.tools import build_entrypoint_parsers


@handle_cli_errors
def entrypoint(cliargs: Namespace) -> int:
    controller = ReleaseController()
    controller.release()
    return 0


def configure_parser(subparser: Any) -> None:
    build_entrypoint_parsers(
        subparser=subparser,
        name="release",
        root_help="Make releases for a pytoolbelt.",
        entrypoint=entrypoint
    )
