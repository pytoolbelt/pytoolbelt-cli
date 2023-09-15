from pathlib import Path
from typing import List
from abc import abstractmethod
from pytoolbelt.utils import file_handler


class BaseInitializer:

    def initialize(self) -> None:
        self._create_directories()
        self._create_files()

    @property
    @abstractmethod
    def files(self) -> List[Path]:
        pass

    @property
    @abstractmethod
    def directories(self) -> List[Path]:
        pass

    def _create_directories(self) -> None:
        for path in self.directories:
            file_handler.create_directory(path, parents=True)

    def _create_files(self) -> None:
        for path in self.files:
            file_handler.create_file_if_not_exists(path)
