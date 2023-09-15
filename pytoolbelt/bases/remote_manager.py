from typing import Optional

from abc import ABC, abstractmethod

from pytoolbelt.environment.config import PYTOOBELT_HOST


class BaseRemoteManager(ABC):

    def __init__(self, base_url: Optional[str] = PYTOOBELT_HOST) -> None:
        self._base_url = base_url

    @property
    def base_url(self) -> str:
        return self._base_url

    @property
    @abstractmethod
    def upload_url(self) -> str:
        pass

    @property
    @abstractmethod
    def download_url(self) -> str:
        pass

    @abstractmethod
    def upload(self) -> None:
        pass

    @abstractmethod
    def download(self) -> None:
        pass
