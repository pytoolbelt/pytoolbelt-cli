from pydantic import BaseModel
from typing import Dict, Optional


class RepoConfig(BaseModel):
    url: str
    secret: str
    release_branch: str


class RepoConfigs(BaseModel):
    default: str
    repos: Dict[str, RepoConfig]

    def get_repo(self, name: Optional[str] = None) -> RepoConfig:
        if name is None or name == "default":
            name = self.default
        return self.repos[name]
