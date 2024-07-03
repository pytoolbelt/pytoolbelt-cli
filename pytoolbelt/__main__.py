from pathlib import Path

from dotenv import load_dotenv

from pytoolbelt.cli import parse_args


def main():
    env_path = Path.cwd() / ".env"
    load_dotenv(env_path)
    cliargs = parse_args()
    cliargs.func(cliargs=cliargs)


if __name__ == "__main__":
    main()
