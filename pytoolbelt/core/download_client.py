from pathlib import Path


class EnvironmentDownloader:

    def __init__(self, name: str, python_version: str, destination: Path) -> None:
        self.name = name
        self.destination = destination
        self.python_version = python_version

    @property
    def url(self) -> str:
        p = Path.cwd().parent / "mock_server" / self.python_version / f"{self.name}.meta.yml"
        return p.as_posix()

    def download(self) -> None:
        pass
