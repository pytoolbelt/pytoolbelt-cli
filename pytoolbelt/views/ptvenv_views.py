from .base_view import BaseComponentTableView


class PtVenvInstalledTableView(BaseComponentTableView):
    def __init__(self):
        super().__init__("Installed PtVenvs", ["Name", "Version"])
