from pathlib import Path
from typing import List, Optional, Tuple, Union

from git import Repo
from git.refs import TagReference
from semver import Version

from pytoolbelt.core.data_classes.pytoolbelt_config import RepoConfig
from pytoolbelt.core.exceptions import (
    NotOnReleaseBranchError,
    UnableToReleaseError,
    UncommittedChangesError,
)
from pytoolbelt.environment.config import PYTOOLBELT_PROJECT_ROOT


class GitCommands:
    def __init__(self, repo_config: RepoConfig, root_path: Optional[Path] = None, repo: Optional[Repo] = None) -> None:
        self.repo = repo or Repo(root_path or PYTOOLBELT_PROJECT_ROOT)
        self.repo_config = repo_config

    @classmethod
    def from_repo(cls, repo: Repo, repo_config: RepoConfig) -> "GitCommands":
        return cls(repo_config, repo=repo)

    @staticmethod
    def init_if_not_exists(root_path: Path) -> None:
        if not root_path.joinpath(".git").exists():
            Repo.init(root_path)

    def get_current_branch(self) -> str:
        return self.repo.active_branch.name

    def is_release_branch(self) -> bool:
        return self.get_current_branch() == self.repo_config.release_branch

    def has_untracked_files_in_directory(self, directory: str) -> bool:
        return any(file.startswith(directory) for file in self.repo.untracked_files)

    def raise_if_not_release_branch(self) -> None:
        if not self.is_release_branch():
            current_branch = self.get_current_branch()
            raise NotOnReleaseBranchError(
                f"{current_branch} branch is not the configured release branch {self.repo_config.release_branch}"
            )

    def raise_if_untracked_files(self) -> None:

        if self.has_untracked_files_in_directory("ptvenv"):
            raise UncommittedChangesError(
                "Repo has untracked files in the ptvenv directory. Please commit your changes before tagging a release."
            )

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
        current_branch = self.get_current_branch()

        if self.repo.head.commit.hexsha != self.repo.commit(f"origin/{current_branch}").hexsha:
            raise UnableToReleaseError(
                "Local and remote HEAD are different. Please pull / push the latest changes before tagging a release."
            )

    def tag_release(self, tag_name: str) -> TagReference:
        return self.repo.create_tag(tag_name)

    def push_tag_to_remote(self, tag_ref: TagReference) -> None:
        self.repo.remote("origin").push(tag_ref.path)

    def push_all_tags_to_remote(self) -> None:
        self.repo.git.push("--tags", "origin")

    def fetch_remote_tags(self) -> None:
        self.repo.git.fetch("--tags", "origin")

    def get_local_tags(self, kind: str, as_names: Optional[bool] = False) -> List[Union[TagReference, str]]:
        local_tags = []
        for tag in self.repo.tags:
            if tag.name.startswith(kind):
                if as_names:
                    local_tags.append(tag.name)
                else:
                    local_tags.append(tag)
        return local_tags

    def get_local_tag(self, tag_name: str, kind: str) -> TagReference:
        for t in self.get_local_tags(kind=kind):
            if t.name == tag_name:
                return t
        else:
            raise ValueError(f"Tag {tag_name} not found in local tags")

    def get_remote_tags(self) -> List[TagReference]:
        tags = self.repo.git.ls_remote("--tags", "origin").split("\n")
        tags = [tag.split("\t")[-1] for tag in tags]
        return [TagReference.from_path(self.repo, tag) for tag in tags]

    def checkout_tag(self, tag_ref: TagReference) -> None:
        self.repo.git.checkout(tag_ref)

    @staticmethod
    def group_versions(tag_refs: List[TagReference], target_name: Optional[str] = None) -> dict:
        result = {}

        for tag_ref in tag_refs:
            try:
                prefix, name, version = tag_ref.name.split("-", 2)
                if target_name and name != target_name:
                    continue
            except ValueError:
                continue

            if prefix not in result:
                result[prefix] = {}

            if name not in result[prefix]:
                result[prefix][name] = {}
                result[prefix][name]["versions"] = []

            result[prefix][name]["versions"].append(Version.parse(version))

        for prefix in result:
            for name in result[prefix]:
                result[prefix][name]["versions"].sort(reverse=True)

        return result

    def local_tags_to_push(self) -> List[TagReference]:
        local_tags = self.get_local_tags()
        remote_tags = self.get_remote_tags()
        local_tags = self.group_versions(local_tags)
        remote_tags = self.group_versions(remote_tags)

        tags_to_push = []
        for prefix in local_tags:
            for name in local_tags[prefix]:
                for version in local_tags[prefix][name]["versions"]:
                    try:
                        if version not in remote_tags[prefix][name]["versions"]:
                            tags_to_push.append(f"{prefix}-{name}-{version}")
                    except KeyError:
                        tags_to_push.append(f"{prefix}-{name}-{version}")

        return [TagReference.from_path(self.repo, f"refs/tags/{tag}") for tag in tags_to_push]

    @staticmethod
    def clone_repo_to_temp_dir(url: str, tmp_dir: str) -> Tuple[Repo, Path]:
        repo = Repo.clone_from(url=url, to_path=tmp_dir)
        return repo, Path(tmp_dir)
