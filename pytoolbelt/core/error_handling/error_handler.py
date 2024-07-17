import functools

from pytoolbelt.environment.config import PYTOOLBELT_DEBUG
from pytoolbelt.core.error_handling import exceptions


class ErrorHandler:
    def __init__(self) -> None:
        self.debug = PYTOOLBELT_DEBUG

    def handle(self, exception: Exception, message: str) -> int:
        print(message)
        return self.reraise_if_debug(exception)

    def reraise_if_debug(self, exception: Exception) -> int:
        """Reraise exception if we are debugging."""
        if self.debug:
            raise exception
        else:
            return 1


def handle_cli_errors(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        error_handler = ErrorHandler()

        try:
            return func(*args, **kwargs)

        except PermissionError as e:
            return error_handler.handle(e, f"pytoolbelt :: Unable to perform action :: Permission denied")

        except FileNotFoundError as e:
            return error_handler.handle(e, f"pytoolbelt :: Unable to perform action :: File not found")

        except OSError as e:
            return error_handler.handle(e, f"pytoolbelt :: Unable to perform action :: Unknown error")

        except exceptions.NotPytoolbeltProjectError as e:
            return error_handler.handle(e, f"pytoolbelt :: ERROR :: {e.args[0]}")

    return wrapper
