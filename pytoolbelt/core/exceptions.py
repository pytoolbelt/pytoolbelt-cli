class PyToolBeltException(Exception):
    """Base exception for all PyToolBelt exceptions."""
    pass


class PyToolBeltProjectNotFound(PyToolBeltException):
    """Raised when a PyToolBelt project is not found."""
    pass


class ToolExists(PyToolBeltException):
    """Raised when a tool already exists."""
    pass


class ToolNotFound(PyToolBeltException):
    """Raised when a tool is not found."""
    pass


class MetaDataError(PyToolBeltException):
    """Raised when there is an error with the metadata."""
    pass


class InterpreterNotFound(PyToolBeltException):
    """Raised when an interpreter is not found."""
    pass


class PythonEnvBuildError(PyToolBeltException):
    """Raised when there is an error with the pyenv build."""
    pass


class ToolDownloadError(PyToolBeltException):
    """Raised when there is an error with the tool download."""
    pass

class PyEnvExistsError(PyToolBeltException):
    """Raised when a pyenv already exists."""
    pass
