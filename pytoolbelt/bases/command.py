from ramjam.cli import Command

from pytoolbelt.core.error_handlers import ErrorHandler
from pytoolbelt.core.exceptions import PyToolBeltProjectNotFound
from pytoolbelt.core.project import PyToolBeltProject


class PyToolBeltCommand(Command):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.project = PyToolBeltProject()
        self.error_handler = ErrorHandler()

    def validate_project(self) -> None:
        if not self.project.cli_root.raise_if_exists():
            raise PyToolBeltProjectNotFound(f"PyToolBelt project not initialized at {self.project.cli_root}. Run `pytoolbelt init` to initialize a project.")
