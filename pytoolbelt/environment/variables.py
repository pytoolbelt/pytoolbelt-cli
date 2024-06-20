import os
from pathlib import Path

PYTOOLBELT_DEBUG = os.getenv("PYTOOLBELT_DEBUG", "false").lower() == "true"
PYTOOLBELT_PROJECT_ROOT = Path(os.getenv("PYTOOLBELT_PROJECT_ROOT", os.getcwd()))
PYTOOLBELT_VENV_DIR = Path.home() / ".pytoolbelt" / "environments"
PYTOOLBELT_TOOLS_DIR = Path.home() / ".pytoolbelt" / "tools"
