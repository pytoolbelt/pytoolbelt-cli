from argparse import Namespace
from typing import Any
from pytoolbelt.core.error_handling.error_handler import handle_cli_errors
from pytoolbelt.core.tools import build_entrypoint_parsers
from pytoolbelt.cli.controllers.releases_controller import ReleasesController, ReleasesParameters, COMMON_FLAGS


@handle_cli_errors
def entrypoint(cliargs: Namespace) -> int:
    params = ReleasesParameters.from_cliargs(cliargs)
    controller = ReleasesController()
    controller.releases(
        name=params.name,
        ptvenv=params.ptvenv,
        tools=params.tools,
        _all=params.all
    )
    return 0


def configure_parser(subparser: Any) -> None:
    build_entrypoint_parsers(
        subparser=subparser,
        name="releases",
        root_help="See Releases for a configured pytoolbelt.",
        entrypoint=entrypoint,
        common_flags=COMMON_FLAGS
    )
