import os
from typing import Dict, Any
from pathlib import Path
import yaml

DEFAULT_PYTHON_VERSION = "3.11"
PYTOOBELT_HOST = "http://localhost:8000"
CONFIG_FILE_PATH = Path("~/.pytoolbelt").expanduser() / "config.yml"


class __ConfigParser:

    def __init__(self) -> None:
        self._config = self._load_config()
        self._config = self.expandvars(self._config)
        self._config = self.expanduser(self._config)

    def _load_config(self) -> Dict[str, Any]:
        if not CONFIG_FILE_PATH.exists():
            return {}

        with open(CONFIG_FILE_PATH, "r") as config_file:
            return yaml.safe_load(config_file)

    def expandvars(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively expand environment variables in string values inside the given dictionary.

        Args:
            data (Dict[str, Any]): Dictionary containing data. String values within the dictionary
                                   can contain environment variable placeholders.

        Returns:
            Dict[str, Any]: Dictionary with expanded environment variables in its string values.
        """
        for key, value in data.items():
            if isinstance(value, dict):
                data[key] = self.expandvars(value)
            elif isinstance(value, list):
                data[key] = [self.expandvars(item) if isinstance(item, dict) else item for item in value]
            elif isinstance(value, str):
                data[key] = os.path.expandvars(value)

        return data

    def expanduser(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively expand user directory `~` or `~user` constructs in string values inside the given dictionary.

        Args:
            data (Dict[str, Any]): Dictionary containing data. String values within the dictionary
                                   can contain user directory placeholders.

        Returns:
            Dict[str, Any]: Dictionary with expanded user directories in its string values.
        """
        for key, value in data.items():
            if isinstance(value, dict):
                data[key] = self.expanduser(value)
            elif isinstance(value, list):
                data[key] = [self.expanduser(item) if isinstance(item, dict) else item for item in value]
            elif isinstance(value, str):
                data[key] = os.path.expanduser(value)

        return data


class Config(__ConfigParser):

    def __init__(self) -> None:
        super().__init__()



class ProjectTree:
    ROOT_DIRECTORY = Path("~/.pytoolbelt").expanduser()
    TOOLS_DIRECTORY = ROOT_DIRECTORY / "tools"
    ENVIRONMENTS_DIRECTORY = ROOT_DIRECTORY / "environments"
    ENVIRONMENTS_METADATA_DIRECTORY = ENVIRONMENTS_DIRECTORY / "metadata"
    BIN_DIRECTORY = ROOT_DIRECTORY / "bin"
    TEMP_DIRECTORY = ROOT_DIRECTORY / "temp"
