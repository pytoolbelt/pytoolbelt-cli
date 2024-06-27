from pathlib import Path
from typing import List
from abc import ABC, abstractmethod


class BasePaths(ABC):

    def __init__(self, root_path: Path, name: str, kind: str) -> None:
        self._root_path = root_path
        self._name = name
        self._kind = kind

    @property
    @abstractmethod
    def new_directories(self) -> List[Path]:
        pass

    @property
    @abstractmethod
    def new_files(self) -> List[Path]:
        pass

    @property
    def root_path(self) -> Path:
        return self._root_path

    @property
    def name(self) -> str:
        return self._name

    @property
    def kind(self) -> str:
        return self._kind

    @staticmethod
    def dir_empty(directory: Path) -> bool:
        return not any(directory.iterdir())

    def create_new_directories(self) -> None:
        for directory in self.new_directories:
            directory.mkdir(parents=True, exist_ok=True)

    def create_new_files(self) -> None:
        for file in self.new_files:
            file.touch(exist_ok=True)

    def create(self) -> None:
        self.create_new_directories()
        self.create_new_files()
