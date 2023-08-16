import functools
from typing import Optional
from pytoolbelt.terminal.environment.variables import PYTOOLBELT_DEBUG
from . import exceptions


class ErrorHandler:

    def __init__(self, debug: Optional[bool] = False) -> None:
        self.debug = debug or PYTOOLBELT_DEBUG

    def handle(self, exception: Exception, message: str) -> int:
        print(message)
        return self.reraise_if_debug(exception)

    def reraise_if_debug(self, exception: Exception) -> int:
        """Reraise exception if we are debugging."""
        if self.debug:
            raise exception
        else:
            return 1


def handle_errors(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):

        try:
            return func(*args, **kwargs)

        except PermissionError as e:
            return args[0].error_handler.handle(e, f"PyToolBelt :: Unable to perform action :: Permission denied")

        except FileNotFoundError as e:
            return args[0].error_handler.handle(e, f"PyToolBelt :: Unable to perform action :: File not found")

        except OSError as e:
            return args[0].error_handler.handle(e, f"PyToolBelt :: Unable to perform action :: Unknown error")

        except exceptions.ToolNotFound as e:
            return args[0].error_handler.handle(e, e.args[0])

        except exceptions.MetaDataError as e:
            return args[0].error_handler.handle(e, e.args[0])

        except exceptions.InterpreterNotFound as e:
            return args[0].error_handler.handle(e, e.args[0])

        except exceptions.PyToolBeltProjectNotFound as e:
            return args[0].error_handler.handle(e, e.args[0])

        except exceptions.ToolExists as e:
            return args[0].error_handler.handle(e, e.args[0])

        except exceptions.PythonEnvBuildError as e:
            return args[0].error_handler.handle(e, e.args[0])

        except exceptions.PyEnvExistsError as e:
            return args[0].error_handler.handle(e, e.args[0])

    return wrapper
