from argparse import Namespace
from typing import Any
from pytoolbelt.controllers import project_controller as pc
from pytoolbelt.core.build_entrypoint_parser import build_entrypoint_parsers
from pytoolbelt.core.error_handler import handle_cli_errors


@handle_cli_errors
def entrypoint(cliargs: Namespace) -> int:
    params = pc.ProjectParameters.from_cliargs(cliargs)
    context = pc.ProjectContext(params)
    action = pc.ACTIONS[params.action]["func"]
    return action(context)


def configure_parser(subparser: Any) -> None:
    build_entrypoint_parsers(
        subparser=subparser,
        name="project",
        root_help="Interact with pytoolbelt project",
        entrypoint=entrypoint,
        actions=pc.ACTIONS,
        common_flags=pc.COMMON_FLAGS,
    )
