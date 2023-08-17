from ramjam.cli import Command
from pytoolbelt.core.project import PyToolBeltProject
from pytoolbelt.core.error_handler.exceptions import PyToolBeltProjectNotFound
from pytoolbelt.core.error_handler import ErrorHandler


class PyToolBeltCommand(Command):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.project = PyToolBeltProject()
        self.error_handler = ErrorHandler()

    def validate_project(self) -> None:
        if not self.project.root.exists():
            raise PyToolBeltProjectNotFound(f"PyToolBelt project not initialized at {self.project.root}. Run `pytoolbelt init` to initialize a project.")
