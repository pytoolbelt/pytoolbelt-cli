from functools import wraps

import yaml
from pydantic import BaseModel

from pytoolbelt.core.error_handling.exceptions import PytoolbeltConfigNotFoundError
from pytoolbelt.environment.config import PYTOOLBELT_DEFAULT_CONFIG_FILE


class PytoolbeltConfig(BaseModel):
    python: str
    bump: str
    envfile: str
    release_branch: str

    @classmethod
    def load(cls) -> "PytoolbeltConfig":
        try:
            with PYTOOLBELT_DEFAULT_CONFIG_FILE.open("r") as file:
                config = yaml.safe_load(file)["project-config"]
        except FileNotFoundError:
            raise PytoolbeltConfigNotFoundError("Pytoolbelt config file not found")
        return cls(**config)


def pytoolbelt_config(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        ptc = PytoolbeltConfig.load()
        return func(*args, **kwargs, ptc=ptc)

    return wrapper
