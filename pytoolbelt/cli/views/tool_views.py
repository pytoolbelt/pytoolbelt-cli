from pytoolbelt.core.data_classes.toolbelt_config import ToolbeltConfig

from .base_view import BaseTableView


class ToolInstalledTableView(BaseTableView):
    def __init__(self):
        super().__init__(
            title="Installed Tools",
            headers=[
                {"header": "Name", "style": "cyan", "justify": "right"},
                {"header": "Version", "style": "magenta", "justify": "center"},
                {"header": "Path", "style": "green"},
            ],
        )

    def add_row(self, name: str, version: str, path: str) -> None:
        super().add_row(name, str(version), path)


class ToolReleasesTableView(BaseTableView):
    def __init__(self, repo_config: ToolbeltConfig) -> None:
        self.repo_config = repo_config
        super().__init__(
            title="PtVenv Releases",
            headers=[
                {"header": "Name", "style": "cyan", "justify": "right"},
                {"header": "Version", "style": "magenta", "justify": "center"},
                {"header": "Release Date", "style": "green", "justify": "center"},
                {"header": "Release Link", "style": "red"},
            ],
        )

    def add_row(self, name: str, version: str, release_date: str, commit: str) -> None:
        url = self.format_commit_url(name, version, commit)
        super().add_row(name, version, release_date, url)

    def format_commit_url(self, name: str, version: str, commit: str) -> str:
        url = f"https://github.com/{self.repo_config.owner}/{self.repo_config.repo_name}/tree/{commit}/tools/{name}"
        display_text = f"View on GitHub -- {name}-{version}"
        return f"[link={url}]{display_text}[/link]"
