"""
TODO: Add tests
"""

import os
from pathlib import Path
from typing import Dict, Optional

import giturlparse
import yaml
from pydantic import BaseModel

from pytoolbelt.core.error_handling.exceptions import PytoolbeltError
from pytoolbelt.environment.config import (
    PYTOOLBELT_TOOLBELT_CONFIG_FILE,
    PYTOOLBELT_TOOLBELT_INSTALL_DIR,
)


class ToolbeltConfig(BaseModel):
    url: str
    owner: str
    name: str
    release_branch: str = "main"
    path: Path

    @classmethod
    def from_url(cls, url: str, path: Optional[Path] = None) -> "ToolbeltConfig":
        parsed_url = giturlparse.parse(url)
        if not path:
            path = PYTOOLBELT_TOOLBELT_INSTALL_DIR / parsed_url.name
        return cls(url=url, owner=parsed_url.owner, name=parsed_url.name, path=path)

    @classmethod
    def from_name_owner(cls, name: str, owner: str) -> "ToolbeltConfig":
        return cls(
            url=f"git@github.com:{owner}/{name}.git",
            owner=owner,
            name=name,
        )

    def to_dict(self) -> Dict[str, str]:
        return {
            "url": self.url,
            "owner": self.owner,
            "name": self.name,
            "release_branch": self.release_branch,
            "path": str(self.path),
        }


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
            raise PytoolbeltError(f"Directory {key} not in toolbelts.yml file. Did you provide the --toolbelt flag?")

    def add(self, repo: ToolbeltConfig) -> None:
        self.repos[repo.name] = repo

    def save(self) -> None:
        with PYTOOLBELT_TOOLBELT_CONFIG_FILE.open("w") as file:
            yaml.safe_dump({"repos": {name: repo.to_dict() for name, repo in self.repos.items()}}, file)
