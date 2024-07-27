import shlex
from subprocess import Popen, PIPE
from pytoolbelt.core.data_classes.toolbelt_config import ToolbeltConfig
from pytoolbelt.core.project.toolbelt_components import ToolbeltPaths
from pytoolbelt.core.error_handling.exceptions import PytoolbeltError


class BaseRuffFormatter(Popen):

    def __init__(self, toolbelt: ToolbeltConfig, raw_command: str) -> None:
        self.toolbelt = toolbelt
        self.paths = ToolbeltPaths(toolbelt.path)
        self.raw_command = raw_command
        super().__init__(args=shlex.split(self.raw_command), stderr=PIPE, stdout=PIPE)

    def run(self):
        output, error = self.communicate()

        if self.returncode != 0:
            error_message = error.decode() if error else "Unknown error"
            raise PytoolbeltError(f"Error while running ruff: {error_message} (Exit code: {self.returncode})")

        for line in output.decode().splitlines():
            print(line)


class RuffFormatter(BaseRuffFormatter):

    def __init__(self, toolbelt: ToolbeltConfig):
        paths = ToolbeltPaths(toolbelt.path)
        raw_command = f"ruff format {paths.tools_dir}"
        super().__init__(toolbelt, raw_command)


class RuffInputSorter(BaseRuffFormatter):

    def __init__(self, toolbelt: ToolbeltConfig):
        paths = ToolbeltPaths(toolbelt.path)
        raw_command = f"ruff check {paths.tools_dir} --select I --fix"
        super().__init__(toolbelt, raw_command)
