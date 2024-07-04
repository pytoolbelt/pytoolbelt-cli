from .base_view import BaseComponentTableView


class ToolInstalledTableView(BaseComponentTableView):
    def __init__(self):
        super().__init__("Installed Tools", ["Name", "Version"])
