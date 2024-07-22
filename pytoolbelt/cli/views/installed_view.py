from pytoolbelt.cli.views.base_view import BaseTableView
from pytoolbelt.core.error_handling.exceptions import PytoolbeltError


class InstalledTableView(BaseTableView):
    def __init__(self, ptvenv: bool, tools: bool) -> None:
        self.ptvenv = ptvenv
        self.tools = tools

        if self.ptvenv:
            title = "Installed PtVenvs"
        elif self.tools:
            title = "Installed Tools"
        else:
            raise PytoolbeltError("Must specify either --ptvenv or --tools")

        super().__init__(
            title=title,
            headers=[
                {"header": "Name", "style": "cyan", "justify": "right"},
                {"header": "Version", "style": "magenta", "justify": "center"},
                {"header": "Path", "style": "green"},
            ],
        )

    def add_row(self, name: str, version: str, path: str) -> None:
        super().add_row(name, str(version), path)
