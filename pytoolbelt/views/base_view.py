from typing import Tuple

from prettytable import PrettyTable
from semver import Version


class BaseTableView:
    def __init__(self, title: str, headers: list[str]):
        self.title = title
        self.headers = headers
        self.table = PrettyTable()
        self.table.title = title
        self.table.field_names = headers

    def add_row(self, *row):
        self.table.add_row(row)

    def print_table(self):
        self.table.align = "l"
        print(self.table)


class BaseComponentTableView(BaseTableView):
    def __init__(self, title: str, headers: list[str]):
        super().__init__(title, headers)

    def add_row(self, name: str, version: Version) -> None:
        super().add_row(name, str(version))
