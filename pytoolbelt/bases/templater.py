from jinja2 import Environment, PackageLoader
from typing import List, Callable


class BaseTemplater:

    def __init__(self):
        self.jinja = self.get_jinja_env()

    @staticmethod
    def get_jinja_env() -> Environment:
        return Environment(loader=PackageLoader("pytoolbelt", "templates"))

    def get_template_methods(self) -> List[Callable]:
        return [getattr(self, method_name) for method_name in dir(self) if method_name.startswith("_template")]

    def template(self) -> None:
        for template_method in self.get_template_methods():
            template_method()

    def _render_template(self, template_name: str, **kwargs) -> str:
        template = self.jinja.get_template(template_name)
        return template.render(**kwargs)
