from abc import ABC, abstractmethod
from jinja2 import Environment, PackageLoader


class BaseTemplater(ABC):

    def __init__(self):
        self.jinja = self.get_jinja_env()

    @staticmethod
    def get_jinja_env() -> Environment:
        return Environment(loader=PackageLoader("pytoolbelt", "templates"))

    @abstractmethod
    def template(self) -> None:
        pass
