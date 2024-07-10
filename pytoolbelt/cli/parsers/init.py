from argparse import Namespace
from typing import Any

from pytoolbelt.cli.controllers.init_controller import InitController
from pytoolbelt.core.error_handling.error_handler import handle_cli_errors
from pytoolbelt.core.tools import build_entrypoint_parsers


@handle_cli_errors
def entrypoint(cliargs: Namespace) -> int:
    return InitController.init_project(path=cliargs.path)


def configure_parser(subparser: Any) -> None:
    build_entrypoint_parsers(
        subparser=subparser,
        name="init",
        root_help="Initialize .pytoolbelt home directory",
        entrypoint=entrypoint,
        common_flags={"--path": {"help": "Add .pytoolbelt/tools to $PATH", "action": "store_true", "default": False}},
    )
