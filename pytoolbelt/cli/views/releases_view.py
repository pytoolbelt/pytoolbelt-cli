from pytoolbelt.cli.views.base_view import BaseTableView
from pytoolbelt.core.data_classes.toolbelt_config import ToolbeltConfig


class ReleasesTableView(BaseTableView):
    def __init__(self, toolbelt: ToolbeltConfig, ptvenv: bool, tools: bool, _all: bool) -> None:
        self.toolbelt = toolbelt
        self.ptvenv = ptvenv
        self.tools = tools
        self.all = _all

        if self.ptvenv:
            title = f"PtVenv Releases for {toolbelt.name} {toolbelt.url}"
            self.component = "ptvenv"
        elif self.tools:
            title = f"Tools Releases for {toolbelt.name} {toolbelt.url}"
            self.component = "tools"
        else:
            raise ValueError("Must specify either --ptvenv or --tools")

        super().__init__(
            title=title,
            headers=[
                {"header": "Name", "style": "cyan", "justify": "right"},
                {"header": "Version", "style": "magenta", "justify": "center"},
                {"header": "Release Date", "style": "green", "justify": "center"},
                {"header": "Release Link", "style": "red"},
            ],
        )

    def add_row(self, name: str, version: str, release_date: str, commit: str) -> None:
        url = self.format_commit_url(name, version, commit)
        super().add_row(name, str(version), release_date, url)

    def format_commit_url(self, name: str, version: str, commit: str) -> str:
        url = f"https://github.com/{self.toolbelt.owner}/{self.toolbelt.name}/tree/{commit}/{self.component}/{name}"
        display_text = f"View Release -- {name}-{version}"
        return f"[link={url}]{display_text}[/link]"
