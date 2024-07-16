from argparse import Namespace
from typing import Any

from pytoolbelt.cli.controllers.installed_controller import (
    COMMON_FLAGS,
    InstalledController,
    InstalledParameters,
)
from pytoolbelt.core.error_handling.error_handler import handle_cli_errors
from pytoolbelt.core.tools import build_entrypoint_parsers


@handle_cli_errors
def entrypoint(cliargs: Namespace) -> int:
    params = InstalledParameters.from_cliargs(cliargs)
    controller = InstalledController()
    return controller.installed(ptvenv=params.ptvenv, tools=params.tools)


def configure_parser(subparser: Any) -> None:
    build_entrypoint_parsers(
        subparser=subparser,
        name="installed",
        root_help="See installed components from any pytoolbelt",
        entrypoint=entrypoint,
        common_flags=COMMON_FLAGS,
    )
