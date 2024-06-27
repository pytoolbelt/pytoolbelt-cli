from typing import Generic, TypeVar
from .baseparameters import BaseControllerParameters

T = TypeVar('T', bound=BaseControllerParameters)


class BaseContext(Generic[T]):
    def __init__(self, params: T) -> None:
        self._params = params

    @property
    def params(self) -> T:
        return self._params
