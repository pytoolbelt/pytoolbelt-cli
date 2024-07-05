from .base_view import BaseComponentTableView, BaseTableView
from ..core.data_classes.pytoolbelt_config import RepoConfig


class PtVenvInstalledTableView(BaseComponentTableView):
    def __init__(self):
        super().__init__("Installed PtVenvs", ["Name", "Version"])


class PtVenvReleasesTableView(BaseTableView):
    def __init__(self, repo_config: RepoConfig) -> None:
        self.repo_config = repo_config
        super().__init__(
            title="PtVenv Releases",
            headers=[
                {"header": "Name", "style": "cyan", "justify": "right"},
                {"header": "Version", "style": "magenta", "justify": "center"},
                {"header": "Release Date", "style": "green", "justify": "center"},
                {"header": "Release Link", "style": "red"},
            ])

    def add_row(self, name: str, version: str, release_date: str, commit: str) -> None:
        url = self.format_commit_url(name, version, commit)
        super().add_row(name, version, release_date, url)

    def format_commit_url(self, name: str, version: str, commit: str) -> str:
        # https://github.com/pytoolbelt/pytoolbelt-playground/tree/222fb90b677e0eb4ab942e66a9d382f244aa3816/ptvenv/scum
        url = f"https://github.com/{self.repo_config.owner}/{self.repo_config.repo_name}/tree/{commit}/ptvenv/{name}"
        display_text = f"View on GitHub -- {name}-{version}"
        return f"[link={url}]{display_text}[/link]"
