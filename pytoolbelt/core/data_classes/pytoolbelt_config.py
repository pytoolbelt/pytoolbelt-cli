from pytoolbelt.environment.config import PYTOOLBELT_DEFAULT_CONFIG_FILE
from pydantic import BaseModel
import yaml
from functools import wraps


class PytoolbeltConfig(BaseModel):
    python: str
    bump: str
    envfile: str
    release_branch: str

    @classmethod
    def load(cls) -> "PytoolbeltConfig":
        with PYTOOLBELT_DEFAULT_CONFIG_FILE.open("r") as file:
            config = yaml.safe_load(file)["project-config"]
        return cls(**config)


def pytoolbelt_config(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        ptc = PytoolbeltConfig.load()
        return func(*args, **kwargs, ptc=ptc)
    return wrapper
