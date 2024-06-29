import os
import yaml
from pydantic import BaseModel
from typing import Dict, Optional
from pytoolbelt.core.exceptions import RepoConfigNotFoundError


class RepoConfig(BaseModel):
    url: str
    secret: Optional[str] = None
    release_branch: Optional[str] = "master"


class RepoConfigs(BaseModel):
    default: str
    repos: Dict[str, RepoConfig]

    @classmethod
    def from_yml(cls, raw_yml: str) -> "RepoConfigs":
        raw_data = os.path.expandvars(raw_yml)
        yml = yaml.safe_load(raw_data)
        repos = {name: RepoConfig(**repo) for name, repo in yml["repos"].items() if name != "default"}
        return cls(default=yml["repos"]["default"], repos=repos)

    def get_repo_config(self, name: Optional[str] = None) -> RepoConfig:
        if name is None or name == "default":
            name = self.default
        try:
            return self.repos[name]
        except KeyError:
            raise RepoConfigNotFoundError(name)
