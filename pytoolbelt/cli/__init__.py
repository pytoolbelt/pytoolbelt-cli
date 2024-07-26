import argparse

from pytoolbelt.cli.parsers import (
    init,
    installed,
    ptvenv,
    release,
    releases,
    tool,
    toolbelt,
)

__version__ = "0.4.0"


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--version", action="version", version=f"pytoolbelt :: Version :: {__version__}")

    sub_parsers = parser.add_subparsers(dest="command")
    sub_parsers.required = True

    commands = [ptvenv, toolbelt, tool, init, releases, installed, release]
    commands.sort(key=lambda x: x.__name__)

    for command in commands:
        command.configure_parser(sub_parsers)

    return parser.parse_args()
