from argparse import Namespace
from typing import Any

from pytoolbelt.controllers import project_controller
from pytoolbelt.core.build_entrypoint_parser import build_entrypoint_parsers
from pytoolbelt.core.error_handler import handle_cli_errors


@handle_cli_errors
def entrypoint(cliargs: Namespace) -> int:
    params = project_controller.ProjectParameters.from_cliargs(cliargs)
    context = project_controller.ProjectContext(params)
    action = project_controller.ACTIONS[params.action]["func"]
    return action(context)


def configure_parser(subparser: Any) -> None:
    build_entrypoint_parsers(
        subparser=subparser,
        name="project",
        root_help="Interact with the pytoolbelt project",
        entrypoint=entrypoint,
        actions=project_controller.ACTIONS,
        common_flags=project_controller.COMMON_FLAGS,
    )
