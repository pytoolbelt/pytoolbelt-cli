from argparse import Namespace
from typing import Any

from pytoolbelt.cli.controllers.format_controller import (
    COMMON_FLAGS,
    FormatController,
    FormatParameters,
)
from pytoolbelt.core.error_handling.error_handler import handle_cli_errors
from pytoolbelt.core.tools import build_entrypoint_parsers


@handle_cli_errors
def entrypoint(cliargs: Namespace) -> int:
    params = FormatParameters.from_cliargs(cliargs)
    controller = FormatController()
    controller.format(params=params)
    return 0


def configure_parser(subparser: Any) -> None:
    build_entrypoint_parsers(
        subparser=subparser,
        name="format",
        root_help="Format tools in a pytoolbelt.",
        entrypoint=entrypoint,
        common_flags=COMMON_FLAGS,
    )
