from functools import wraps
from pathlib import Path
import yaml
from pydantic import BaseModel

from pytoolbelt.core.error_handling.exceptions import PytoolbeltConfigNotFoundError
from pytoolbelt.environment.config import PYTOOLBELT_DEFAULT_CONFIG_FILE
from pytoolbelt.core.data_classes.toolbelt_config import ToolbeltConfigs


class PytoolbeltConfig(BaseModel):
    python: str
    bump: str
    envfile: str
    release_branch: str

    @classmethod
    def load(cls, root_path: Path) -> "PytoolbeltConfig":
        config_path = root_path / "pytoolbelt.yml"
        try:
            with config_path.open("r") as file:
                config = yaml.safe_load(file)["project-config"]
        except FileNotFoundError:
            raise PytoolbeltConfigNotFoundError("Pytoolbelt config file not found")
        return cls(**config)


def pytoolbelt_config(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        toolbelt = ToolbeltConfigs.load().get(kwargs["params"].toolbelt)
        ptc = PytoolbeltConfig.load(toolbelt.path)
        return func(*args, **kwargs, ptc=ptc, toolbelt=toolbelt)
    return wrapper
