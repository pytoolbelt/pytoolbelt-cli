class PyToolBeltException(Exception):
    """Base exception for all PyToolBelt exceptions."""
    pass


class PyToolBeltProjectNotFound(PyToolBeltException):
    """Raised when a PyToolBelt project is not found."""
    pass


class ToolExistsError(PyToolBeltException):
    """Raised when a tool already raise_if_exists."""
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
    """Raised when a pyenv already raise_if_exists."""
    pass


class PyEnvDownloadError(PyToolBeltException):
    """Raised when there is an error with the pyenv download."""
    pass


class PyEnvUploadError(PyToolBeltException):
    """Raised when there is an error with the pyenv upload."""
    pass
