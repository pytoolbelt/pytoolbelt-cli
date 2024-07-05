from typing import Dict
from pytoolbelt.environment.config import PYTOOLBELT_GLOBAL_CONFIG_FILE
import yaml
from pydantic import BaseModel

from pytoolbelt.core.error_handling.exceptions import RepoConfigNotFoundError


class RepoConfig(BaseModel):
    url: str
    owner: str
    name: str


class RepoConfigs(BaseModel):
    repos: Dict[str, RepoConfig]

    @classmethod
    def load(cls) -> "RepoConfigs":
        with PYTOOLBELT_GLOBAL_CONFIG_FILE.open("r") as file:
            config = yaml.safe_load(file)["repos"]
            repos = {name: RepoConfig(**repo) for name, repo in config.items()}
        return cls(repos=repos)

    def get(self, key: str) -> RepoConfig:
        try:
            return self.repos[key]
        except KeyError:
            raise RepoConfigNotFoundError(f"Repo {key} not found in pytoolbelt-config.yml file")
