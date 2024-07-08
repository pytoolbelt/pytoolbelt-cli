from typing import Dict
from pytoolbelt.environment.config import PYTOOLBELT_TOOLBELT_CONFIG_FILE
import yaml
from pydantic import BaseModel
import giturlparse
from pytoolbelt.core.error_handling.exceptions import RepoConfigNotFoundError
import os


class ToolbeltConfig(BaseModel):
    url: str
    owner: str
    name: str

    @classmethod
    def from_url(cls, url: str) -> "ToolbeltConfig":
        parsed_url = giturlparse.parse(url)
        return cls(url=url, owner=parsed_url.owner, name=parsed_url.name)

    @classmethod
    def from_name_owner(cls, name: str, owner: str) -> "ToolbeltConfig":
        return cls(
            url=f"https://github.com/{owner}/{name}.git",
            owner=owner,
            name=name,
        )


class ToolbeltConfigs(BaseModel):
    repos: Dict[str, ToolbeltConfig]

    @classmethod
    def load(cls) -> "ToolbeltConfigs":
        with PYTOOLBELT_TOOLBELT_CONFIG_FILE.open("r") as file:
            raw_data = os.path.expandvars(file.read())
            config = yaml.safe_load(raw_data)["repos"]
            if not config:
                config = {}
            repos = {name: ToolbeltConfig(**repo) for name, repo in config.items()}
        return cls(repos=repos)

    def get(self, key: str) -> ToolbeltConfig:
        try:
            return self.repos[key]
        except KeyError:
            raise RepoConfigNotFoundError(f"Repo {key} not found in pytoolbelt-config.yml file")

    def add(self, repo: ToolbeltConfig) -> None:
        self.repos[repo.name] = repo

    def save(self) -> None:
        with PYTOOLBELT_TOOLBELT_CONFIG_FILE.open("w") as file:
            yaml.safe_dump({"repos": {name: dict(repo) for name, repo in self.repos.items()}}, file)
