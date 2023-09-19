import functools
import requests
from typing import Optional, Type, Callable
from pytoolbelt.environment.variables import PYTOOLBELT_DEBUG
from pytoolbelt.core import exceptions


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


def handle_cli_errors(func):
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

        except exceptions.PyToolBeltProjectNotFound as e:
            return args[0].error_handler.handle(e, e.args[0])

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


def handle_http_errors(exception: Type[Exception], msg: str) -> Callable:
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            try:
                response = func(*args, **kwargs)
                response.raise_for_status()  # Raise an HTTPError for bad responses
                return response

            except requests.exceptions.HTTPError as e:
                raise exception(f"{msg}HTTP error occurred. {str(e.args[0])}")
            except requests.exceptions.ConnectionError:
                raise exception(f"{msg}Network-related connection error occurred.")
            except requests.exceptions.Timeout:
                raise exception(f"{msg}Request timed out.")
            except requests.exceptions.TooManyRedirects:
                raise exception(f"{msg}Too many redirects.")
            except requests.exceptions.RequestException as e:
                raise exception(f"{msg}An unknown error occurred making the http request. {str(e)}")
        return wrapper
    return decorator
