from functools import wraps
from pathlib import Path
from typing import Optional

import yaml
from pydantic import BaseModel

from pytoolbelt.core.data_classes.toolbelt_config import ToolbeltConfigs
from pytoolbelt.core.error_handling.exceptions import PytoolbeltError


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
            raise PytoolbeltError("Pytoolbelt config file not found")
        return cls(**config)


def pytoolbelt_config(provide_ptc: Optional[bool] = False):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            toolbelt = ToolbeltConfigs.load().get(kwargs["params"].toolbelt)
            if provide_ptc:
                ptc = PytoolbeltConfig.load(toolbelt.path)
                kwargs["ptc"] = ptc
            return func(*args, **kwargs, toolbelt=toolbelt)

        return wrapper

    return decorator
