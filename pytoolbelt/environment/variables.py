import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

_DEFAULT_USER_DIRECTORY = Path.home() / "pytoolbelt"
_DEFAULT_CLI_DIRECTORY = Path.home() / ".pytoolbelt-cli"

PYTOOLBELT_DEBUG = os.environ.get("PYTOOLBELT_DEBUG", "").lower() == "true"
PYTOOLBELT_DEFAULT_PYTHON_VERSION = os.getenv("PYTOOLBELT_DEFAULT_PYTHON_VERSION", "3.11")
PYTOOBELT_HOST = os.getenv("PYTOOLBELT_HOST", "https://pytoolbelt.com")
PYTOOLBELT_USER_DIRECTORY = os.getenv("PYTOOLBELT_USER_DIRECTORY", _DEFAULT_USER_DIRECTORY)
PYTOOLBELT_CLI_DIRECTORY = os.getenv("PYTOOLBELT_CLI_DIRECTORY", _DEFAULT_CLI_DIRECTORY)
