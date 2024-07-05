from argparse import Namespace
from typing import Any

from pytoolbelt.cli.entrypoints import project_entrypoints
from pytoolbelt.core.tools import build_entrypoint_parsers
from pytoolbelt.core.error_handling.error_handler import handle_cli_errors


@handle_cli_errors
def entrypoint(cliargs: Namespace) -> int:
    params = project_entrypoints.ProjectParameters.from_cliargs(cliargs)
    action = project_entrypoints.ACTIONS[params.action]["func"]
    return action(params=params)


def configure_parser(subparser: Any) -> None:
    build_entrypoint_parsers(
        subparser=subparser,
        name="project",
        root_help="Interact with the pytoolbelt project",
        entrypoint=entrypoint,
        actions=project_entrypoints.ACTIONS,
        common_flags=project_entrypoints.COMMON_FLAGS,
    )
