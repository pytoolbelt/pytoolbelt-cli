import shutil
import tempfile
from pathlib import Path
from typing import List, Optional, Tuple, Union

from git import Repo, TagReference

from pytoolbelt.core.data_classes.toolbelt_config import ToolbeltConfig
from pytoolbelt.core.error_handling.exceptions import PytoolbeltError


class GitClient:
    def __init__(
        self, repo: Repo, config: Optional[ToolbeltConfig] = None, release_branch: Optional[str] = None
    ) -> None:
        self._repo = repo
        self._config = config
        self._release_branch = release_branch

    @classmethod
    def from_path(
        cls, path: Path, config: Optional[ToolbeltConfig] = None, release_branch: Optional[str] = None
    ) -> "GitClient":
        return cls(Repo(path), config, release_branch)

    @staticmethod
    def repo_from_path(path: Path) -> Repo:
        return Repo(path)

    @classmethod
    def clone_from_url(cls, url: str, path: Path) -> "GitClient":
        repo = Repo.clone_from(url, path)
        return cls(repo)

    @staticmethod
    def init_if_not_exists(path: Path) -> Repo:
        if not path.joinpath(".git").exists():
            return Repo.init(path)

    @staticmethod
    def get_tag_filter(kind: str, name: Optional[str] = None) -> str:
        return f"{kind}-{name}-" if name else f"{kind}-"

    @property
    def repo(self) -> Repo:
        return self._repo

    @property
    def repo_config(self) -> Optional[ToolbeltConfig]:
        return self._config

    @property
    def current_branch(self) -> str:
        return self.repo.active_branch.name

    @property
    def release_branch(self) -> str:
        return self._release_branch or self.repo_config.release_branch

    def is_release_branch(self) -> bool:
        if not self.repo_config and not self._release_branch:
            raise PytoolbeltError(
                "No release branch set. Please provide a release branch in a repo config or pytoolbelt.yml."
            )
        return self.current_branch == self.release_branch

    def has_untracked_files_in_directory(self, directory: str) -> bool:
        return any(file.startswith(directory) for file in self.repo.untracked_files)

    def raise_if_not_release_branch(self) -> None:
        if not self.is_release_branch():
            raise PytoolbeltError(
                f"{self.current_branch} branch is not the configured release branch {self.repo_config.release_branch}"
            )

    def raise_if_untracked_ptvenv(self) -> None:

        if self.has_untracked_files_in_directory("ptvenv"):
            raise PytoolbeltError(
                "Repo has untracked files in the ptvenv directory. Please commit your changes before tagging a release."
            )

    def raise_if_untracked_tools(self) -> None:
        if self.has_untracked_files_in_directory("tools"):
            raise PytoolbeltError(
                "Repo has untracked files in the tools directory. Please commit your changes before tagging a release."
            )

    def raise_if_uncommitted_changes(self) -> None:
        if self.repo.is_dirty():
            raise PytoolbeltError("Repo has uncommited changes. Please commit your changes before tagging a release.")

    def raise_if_local_and_remote_head_are_different(self) -> None:
        self.repo.remotes.origin.fetch()
        if self.repo.head.commit.hexsha != self.repo.commit(f"origin/{self.current_branch}").hexsha:
            raise PytoolbeltError(
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

    def ptvenv_releases(
        self, name: Optional[str] = None, as_names: Optional[bool] = False
    ) -> Union[List[TagReference], List[str]]:
        flt = self.get_tag_filter("ptvenv", name)
        if as_names:
            return [tag.name for tag in self.repo.tags if tag.name.startswith(flt)]
        return [tag for tag in self.repo.tags if tag.name.startswith(flt)]

    def tool_releases(
        self, name: Optional[str] = None, as_names: Optional[bool] = False
    ) -> Union[List[TagReference], List[str]]:
        flt = self.get_tag_filter("tool", name)
        if as_names:
            return [tag.name for tag in self.repo.tags if tag.name.startswith(flt)]
        return [tag for tag in self.repo.tags if tag.name.startswith(flt)]

    def get_tag_reference(self, tag_name: str) -> TagReference:
        return self.repo.tags[tag_name]

    def checkout_tag(self, tag_ref: TagReference) -> None:
        self.repo.git.checkout(tag_ref)


class TemporaryGitClient:
    def __init__(self, src: Path, toolbelt: str):
        self._root_tmp_dir = tempfile.TemporaryDirectory()
        self.toolbelt = toolbelt
        self.src = src

    @property
    def tmp_dir(self):
        return Path(self._root_tmp_dir.name) / "pytoolbelt" / self.toolbelt

    def __enter__(self) -> Tuple["TemporaryGitClient", GitClient]:
        shutil.copytree(src=self.src, dst=self.tmp_dir)
        return self, GitClient.from_path(self.tmp_dir)

    def __exit__(self, exc_type, exc_val, exc_tb):
        # TODO: Implement logging....
        try:
            self._root_tmp_dir.cleanup()
        except (PermissionError, OSError):
            pass

        if exc_type:
            return False
        return True
