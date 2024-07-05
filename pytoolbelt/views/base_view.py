from typing import Tuple
from rich.table import Table
from rich.console import Console
from abc import ABC, abstractmethod

from semver import Version


class BaseTableView:
    def __init__(self, title: str, headers: list[dict[str, str]]):
        self.title = title
        self.table = Table(title=title)

        for header in headers:
            self.table.add_column(**header)

    def add_row(self, *row: str):
        self.table.add_row(*row)

    def print_table(self):
        console = Console()
        console.print(self.table)


class BaseComponentTableView(BaseTableView):
    def __init__(self, title: str, headers: list[str]):
        super().__init__(title, headers)

    def add_row(self, name: str, version: Version) -> None:
        super().add_row(name, str(version))
