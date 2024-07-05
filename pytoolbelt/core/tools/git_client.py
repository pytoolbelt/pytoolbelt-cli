from git import Repo, TagReference
from pathlib import Path
from typing import Optional, List, Union, Iterator
from pytoolbelt.core.data_classes.pytoolbelt_config import RepoConfig
from pytoolbelt.core.exceptions import (
    NotOnReleaseBranchError,
    UnableToReleaseError,
    UncommittedChangesError,
)


class GitClient:

    def __init__(self, repo: Repo, config: Optional[RepoConfig] = None) -> None:
        self._repo = repo
        self._config = config

    @classmethod
    def from_path(cls, path: Path, config: Optional[RepoConfig] = None) -> "GitClient":
        return cls(Repo(path), config)

    @staticmethod
    def repo_from_path(path: Path) -> Repo:
        return Repo(path)

    @classmethod
    def clone_from_url(cls, url: str, path: Path) -> "GitClient":
        repo = Repo.clone_from(url, path)
        return cls(repo)

    @staticmethod
    def init_if_not_exists(path: Path) -> None:
        if not path.joinpath(".git").exists():
            Repo.init(path)

    @staticmethod
    def get_tag_filter(kind: str, name: Optional[str] = None) -> str:
        return f"{kind}-{name}-" if name else f"{kind}-"

    @property
    def repo(self) -> Repo:
        return self._repo

    @property
    def repo_config(self) -> Optional[RepoConfig]:
        return self._config

    @property
    def current_branch(self) -> str:
        return self.repo.active_branch.name

    def is_release_branch(self) -> bool:
        return self.current_branch == self.repo_config.release_branch

    def has_untracked_files_in_directory(self, directory: str) -> bool:
        return any(file.startswith(directory) for file in self.repo.untracked_files)

    def raise_if_not_release_branch(self) -> None:
        if not self.is_release_branch():
            raise NotOnReleaseBranchError(
                f"{self.current_branch} branch is not the configured release branch {self.repo_config.release_branch}"
            )

    def raise_if_untracked_ptvenv(self) -> None:

        if self.has_untracked_files_in_directory("ptvenv"):
            raise UncommittedChangesError(
                "Repo has untracked files in the ptvenv directory. Please commit your changes before tagging a release."
            )

    def raise_if_untracked_tools(self) -> None:
        if self.has_untracked_files_in_directory("tools"):
            raise UncommittedChangesError(
                "Repo has untracked files in the tools directory. Please commit your changes before tagging a release."
            )

    def raise_if_uncommitted_changes(self) -> None:
        if self.repo.is_dirty():
            raise UncommittedChangesError(
                "Repo has uncommited changes. Please commit your changes before tagging a release."
            )

    def raise_if_local_and_remote_head_are_different(self) -> None:
        self.repo.remotes.origin.fetch()
        if self.repo.head.commit.hexsha != self.repo.commit(f"origin/{self.current_branch}").hexsha:
            raise UnableToReleaseError(
                "Local and remote HEAD are different. Please pull / push the latest changes before tagging a release."
            )

    def raise_on_release_attempt(self) -> None:
        self.raise_if_not_release_branch()
        self.raise_if_untracked_ptvenv()
        self.raise_if_untracked_tools()
        self.raise_if_uncommitted_changes()
        self.raise_if_local_and_remote_head_are_different()

    def tag_release(self, tag_name: str) -> TagReference:
        return self.repo.create_tag(tag_name)

    def push_tag_to_remote(self, tag_ref: TagReference) -> None:
        self.repo.remote("origin").push(tag_ref.path)

    def push_tags_to_remote(self) -> None:
        self.repo.git.push("--tags", "origin")

    def fetch_remote_tags(self) -> None:
        self.repo.git.fetch("--tags", "origin")

    def ptvenv_releases(self, name: Optional[str] = None, as_names: Optional[bool] = False) -> Union[List[TagReference], List[str]]:
        flt = self.get_tag_filter("ptvenv", name)
        if as_names:
            return [tag.name for tag in self.repo.tags if tag.name.startswith(flt)]
        return [tag for tag in self.repo.tags if tag.name.startswith(flt)]

    def tool_releases(self, name: Optional[str] = None, as_names: Optional[bool] = False) -> Union[List[TagReference], List[str]]:
        flt = self.get_tag_filter("tool", name)
        if as_names:
            return [tag.name for tag in self.repo.tags if tag.name.startswith(flt)]
        return [tag for tag in self.repo.tags if tag.name.startswith(flt)]

    def get_tag_reference(self, tag_name: str) -> TagReference:
        return self.repo.tags[tag_name]

    def checkout_tag(self, tag_ref: TagReference) -> None:
        self.repo.git.checkout(tag_ref)
