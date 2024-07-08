from argparse import Namespace
from typing import Any
from pytoolbelt.core.error_handling.error_handler import handle_cli_errors
from pytoolbelt.environment.config import init_home, add_path


@handle_cli_errors
def entrypoint(cliargs: Namespace) -> int:
    init_home()
    print("Created .pytoolbelt home directory")

    if cliargs.path:
        print("Adding .pytoolbelt/tools to $PATH")
        add_path()
    else:
        print(
            "To add .pytoolbelt/tools to $PATH, run `pytoolbelt init --path` "
            f"or add the following to your shell configuration file: export PATH=~/.pytoolbelt/tools:$PATH"
        )
    return 0


def configure_parser(subparser: Any) -> None:
    command_parser = subparser.add_parser("init", help="Initialize .pytoolbelt home directory")
    command_parser.add_argument("--path", action="store_true", help="Add .pytoolbelt/tools to $PATH", default=False)
    command_parser.set_defaults(func=entrypoint)
