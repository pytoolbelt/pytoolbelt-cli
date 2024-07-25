from typing import Dict, List

from rich.console import Console
from rich.table import Table


class BaseTableView:
    def __init__(self, title: str, headers: List[Dict[str, str]]):
        self.title = title
        self.table = Table(title=title)

        for header in headers:
            self.table.add_column(**header)

    def add_row(self, *row: str):
        self.table.add_row(*row)

    def print_table(self):
        console = Console()
        console.print(self.table)
