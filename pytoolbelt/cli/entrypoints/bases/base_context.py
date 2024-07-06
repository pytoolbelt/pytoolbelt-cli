from typing import Generic, TypeVar

from .base_parameters import BaseEntrypointParameters

T = TypeVar("T", bound=BaseEntrypointParameters)


class BaseContext(Generic[T]):
    def __init__(self, params: T) -> None:
        self._params = params

    @property
    def params(self) -> T:
        return self._params
