from pathlib import Path
from typing import List

import pytest

from pytoolbelt.core.bases.base_paths import BasePaths


class MockBasePaths(BasePaths):
    def __init__(self, root_path: Path):
        super().__init__(root_path)

    @property
    def new_directories(self) -> List[Path]:
        return [self.root_path / "dir1", self.root_path / "dir2"]

    @property
    def new_files(self) -> List[Path]:
        return [self.root_path / "file1.txt", self.root_path / "dir1/file2.txt"]


@pytest.fixture
def base_paths(tmp_path):
    return MockBasePaths(tmp_path)


def test_directory_creation_creates_all_new_directories(base_paths):
    base_paths.create_new_directories()
    assert all(directory.exists() for directory in base_paths.new_directories)


def test_file_creation_creates_all_new_files(base_paths):
    base_paths.create_new_directories()
    base_paths.create_new_files()
    assert all(file.exists() for file in base_paths.new_files)


def test_create_creates_all_new_directories_and_files(base_paths):
    base_paths.create()
    assert all(directory.exists() for directory in base_paths.new_directories)
    assert all(file.exists() for file in base_paths.new_files)


def test_dir_empty_returns_true_for_empty_directory(base_paths, tmp_path):
    empty_dir = tmp_path / "empty_dir"
    empty_dir.mkdir(parents=True, exist_ok=True)
    assert base_paths.dir_empty(empty_dir)


def test_dir_empty_returns_false_for_non_empty_directory(base_paths, tmp_path):
    non_empty_dir = tmp_path / "non_empty_dir"
    non_empty_dir.mkdir(parents=True, exist_ok=True)
    (non_empty_dir / "file.txt").touch()
    assert not base_paths.dir_empty(non_empty_dir)
