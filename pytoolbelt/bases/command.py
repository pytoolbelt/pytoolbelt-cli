from ramjam.cli import Command

from pytoolbelt.core.error_handlers import ErrorHandler
from pytoolbelt.core.exceptions import PyToolBeltProjectNotFound
from pytoolbelt.core.project import PyToolBeltProject


class PyToolBeltCommand(Command):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.project = PyToolBeltProject()
        self.error_handler = ErrorHandler()
        self.validate_project()

    def validate_project(self) -> None:
        project_paths = self.project.get_project_paths()
        if not project_paths.cli_root.exists() or not project_paths.user_root.exists():
            raise PyToolBeltProjectNotFound(f"PyToolBelt project not initialized at Run `pytoolbelt project --init` to initialize a project.")
