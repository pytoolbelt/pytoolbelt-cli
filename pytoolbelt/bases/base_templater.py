from jinja2 import Environment, PackageLoader


class BaseTemplater:
    def __init__(self) -> None:
        self.jinja_env = self.get_jinja_environment()

    @staticmethod
    def get_jinja_environment() -> Environment:
        """
        used to get a jinja2 templating environment.
        Returns: Jinja2 Environment
        """
        loader = PackageLoader(package_name="pytoolbelt", package_path="templates")
        return Environment(loader=loader, trim_blocks=True, lstrip_blocks=True)

    @staticmethod
    def format_template_name(file_name: str) -> str:
        """
        used to format a template name
        Args:
            file_name: name of the file to format
        Returns: formatted template name
        """
        return f"{file_name}.jinja2"

    def render(self, template_name: str, **kwargs) -> str:
        """
        used to render a template
        Args:
            template_name: name of the template to render
            **kwargs: arguments to pass to the template
        Returns: rendered template
        """
        template = self.jinja_env.get_template(template_name)
        return template.render(**kwargs)
