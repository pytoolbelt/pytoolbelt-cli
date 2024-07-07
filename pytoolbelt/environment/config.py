import os
from pathlib import Path

import yaml
from dotenv import load_dotenv
from pydantic import BaseModel

# project paths used for project creation and tool development
PYTOOLBELT_PROJECT_ROOT = Path.cwd()
PYTOOLBELT_TOOLS_ROOT = PYTOOLBELT_PROJECT_ROOT / "tools"
PYTOOLBELT_PTVENV_ROOT = PYTOOLBELT_PROJECT_ROOT / "ptvenv"

# default file paths for config and environment files
PYTOOLBELT_DEFAULT_CONFIG_FILE = PYTOOLBELT_PROJECT_ROOT / "pytoolbelt.yml"
PYTOOLBELT_DEFAULT_ENV_FILE = PYTOOLBELT_PROJECT_ROOT / ".env"

# environment paths used for installation
PYTOOLBELT_VENV_INSTALL_DIR = Path.home() / ".pytoolbelt" / "environments"
PYTOOLBELT_TOOLS_INSTALL_DIR = Path.home() / ".pytoolbelt" / "tools"
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
