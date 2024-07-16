import os
from pathlib import Path
from typing import Optional

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel

# project paths used for project creation and tool development
PYTOOLBELT_TOOLBELT_ROOT = Path.cwd()
PYTOOLBELT_TOOLS_ROOT = PYTOOLBELT_TOOLBELT_ROOT / "tools"
PYTOOLBELT_PTVENV_ROOT = PYTOOLBELT_TOOLBELT_ROOT / "ptvenv"

# default file paths for config and environment files
PYTOOLBELT_DEFAULT_CONFIG_FILE = PYTOOLBELT_TOOLBELT_ROOT / "pytoolbelt.yml"
PYTOOLBELT_DEFAULT_ENV_FILE = PYTOOLBELT_TOOLBELT_ROOT / ".env"

# environment paths used for installation
PYTOOLBELT_VENV_INSTALL_DIR = Path.home() / ".pytoolbelt" / "environments"
PYTOOLBELT_TOOLS_INSTALL_DIR = Path.home() / ".pytoolbelt" / "tools"
PYTOOLBELT_TOOLBELT_INSTALL_DIR = Path.home() / "pytoolbelt" / "toolbelts"
PYTOOLBELT_TOOLBELT_CONFIG_FILE = Path.home() / ".pytoolbelt" / "toolbelt.yml"


# used to set the path to the project config file
# default is the current directory's pytoolbelt.yml file
# however this can be set to an arbitrary path
PYTOOLBELT_PROJECT_CONFIG_FILE_PATH = Path(os.getenv("PYTOOLBELT_CONFIG_FILE_PATH", PYTOOLBELT_DEFAULT_CONFIG_FILE))

PYTOOLBELT_PROJECT_ENV_FILE_PATH = Path(os.getenv("PYTOOLBELT_ENV_FILE_PATH", PYTOOLBELT_DEFAULT_ENV_FILE))


# load the .env file if it exists
if PYTOOLBELT_PROJECT_ENV_FILE_PATH.exists():
    load_dotenv(PYTOOLBELT_PROJECT_ENV_FILE_PATH)

# used to turn on debug logging on and off
PYTOOLBELT_DEBUG = os.getenv("PYTOOLBELT_DEBUG", "false").lower() == "true"


def init_home():
    for directory in [PYTOOLBELT_VENV_INSTALL_DIR, PYTOOLBELT_TOOLS_INSTALL_DIR, PYTOOLBELT_TOOLBELT_INSTALL_DIR]:
        directory.mkdir(parents=True, exist_ok=True)

    for file in [PYTOOLBELT_TOOLBELT_CONFIG_FILE]:
        if not file.exists():
            file.touch(exist_ok=True)
            file.write_text("repos: {}\n")


def add_path() -> None:

    # Check if directory exists
    if not PYTOOLBELT_TOOLS_INSTALL_DIR.exists():
        print(f"Directory {PYTOOLBELT_TOOLS_INSTALL_DIR} does not exist.")
        return

    # Check if directory is already in PATH
    if PYTOOLBELT_TOOLS_INSTALL_DIR.as_posix() in os.environ["PATH"]:
        print(f"Directory {PYTOOLBELT_TOOLS_INSTALL_DIR} is already in PATH.")
        return

    # Determine the shell and corresponding configuration file
    shell = os.environ["SHELL"]
    if shell.endswith("bash"):
        shell_config_file = os.path.expanduser("~/.bash_profile")
    elif shell.endswith("zsh"):
        shell_config_file = os.path.expanduser("~/.zshrc")
    else:
        print(f"Unsupported shell: {shell}")
        return

    # Append export command to shell configuration file
    with open(shell_config_file, "a") as file:
        file.write(f'\nexport PATH="$PATH:{PYTOOLBELT_TOOLS_INSTALL_DIR}"\n')

    print(
        f"Directory {PYTOOLBELT_TOOLS_INSTALL_DIR} added to PATH in {shell}. "
        f"Please restart your shell or run `source {shell_config_file}` for the changes to take effect."
    )


class PyToolBeltConfig(BaseModel):
    python: str
    bump: str

    @classmethod
    def from_pytoolbelt_yml(cls) -> "PyToolBeltConfig":

        if not PYTOOLBELT_PROJECT_CONFIG_FILE_PATH.exists():
            raise FileNotFoundError(f"Config file {PYTOOLBELT_PROJECT_CONFIG_FILE_PATH} does not exist")

        with PYTOOLBELT_PROJECT_CONFIG_FILE_PATH.open("r") as file:
            raw_data = yaml.safe_load(file)
            return cls(**raw_data["pytoolbelt-config"])
