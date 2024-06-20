from git import Repo
from pathlib import Path
from typing import Optional
from pytoolbelt.environment.variables import PYTOOLBELT_PROJECT_ROOT
from pytoolbelt.core.pytoolbelt_config import RepoConfig


class GitCommands:

    def __init__(self, repo_config: RepoConfig, root_path: Optional[Path] = PYTOOLBELT_PROJECT_ROOT) -> None:
        self.repo = Repo(root_path)
        self.repo_config = repo_config

    def get_current_branch(self) -> str:
        return self.repo.active_branch.name

    def is_release_branch(self) -> bool:
        return self.get_current_branch() == self.repo_config.release_branch
