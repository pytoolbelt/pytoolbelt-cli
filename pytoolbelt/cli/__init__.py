import argparse

from pytoolbelt.cli.parsers import add_path, project

__version__ = "0.0.0"


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--version", action="version", version=f"pytoolbelt :: Version :: {__version__}")

    sub_parsers = parser.add_subparsers(dest="command")
    sub_parsers.required = True

    commands = [project]
    commands.sort(key=lambda x: x.__name__)

    for command in commands:
        command.configure_parser(sub_parsers)

    add_path_parser = sub_parsers.add_parser("add-path", help="Add ~/.pytoolbelt/tools to the system PATH")
    add_path_parser.set_defaults(func=add_path.add_path)

    return parser.parse_args()
