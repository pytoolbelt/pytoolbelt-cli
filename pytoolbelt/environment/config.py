import os
from io import StringIO
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


DEFAULT_PYTHON_VERSION = "3.11"
PYTOOBELT_HOST = "http://localhost:8000"
CONFIG_FILE_PATH = Path.home() / ".pytoolbelt-cli" / "config.yml"


class Config:

    def __init__(self, config_path: Optional[Path] = CONFIG_FILE_PATH) -> None:
        self.config_path = config_path
        self.config = self.load_config()

    def load_config(self) -> Dict[str, Any]:
        if self.config_path.exists():
            content = self.config_path.read_text()
            content = os.path.expandvars(content)

            with StringIO(content) as buffer:
                return yaml.safe_load(buffer)
        else:
            return {}

    @property
    def user_root_directory(self) -> Path:
        try:
            return Path(self.config["directories"]["user_root"]).expanduser()
        except KeyError:
            return Path.home() / "pytoolbelt"

    @property
    def cli_root_directory(self) -> Path:
        try:
            return Path(self.config["directories"]["cli_root"]).expanduser()
        except KeyError:
            return Path.home() / ".pytoolbelt-cli"


class ProjectTree:
    _config = Config()
    CLI_ROOT_DIRECTORY = _config.cli_root_directory
    USER_ROOT_DIRECTORY = _config.user_root_directory
    TOOLS_DIRECTORY = _config.user_root_directory / "tools"
    PYENVS_DIRECTORY = _config.user_root_directory / "pyenvs"
    BIN_DIRECTORY = _config.cli_root_directory / "bin"
    ENVIRONMENTS_DIRECTORY = _config.cli_root_directory / "environments"
