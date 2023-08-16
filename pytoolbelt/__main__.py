from ramjam.utils import parse_args
from pytoolbelt.terminal import cli


def main() -> int:

    ignore = [
        "pytoolbeltcommand",
    ]

    cli_args = parse_args(cli, ignore=ignore)

    command = cli_args.command(cli_args=cli_args)

    return command()


if __name__ == "__main__":

    exit_code = main()
    exit(exit_code)
