from jinja2 import Environment, PackageLoader


def get_jinja_env() -> Environment:
    return Environment(loader=PackageLoader("pytoolbelt.terminal", "templates"))
