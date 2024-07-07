from .base_view import BaseTableView
from pytoolbelt.core.data_classes.toolbelt_config import ToolbeltConfigs


class ToolbeltConfigView(BaseTableView):

    def __init__(self) -> None:
        super().__init__(
            title="Pytoolbelt Configuration",
            headers=[
                {"header": "Name", "style": "cyan", "justify": "right"},
                {"header": "Owner", "style": "magenta", "justify": "center"},
                {"header": "URL", "style": "green"},
            ]
        )

    def add_configs(self, configs: ToolbeltConfigs) -> None:
        config_entries = configs.repos.values()
        for config_entry in config_entries:
            self.add_row(config_entry.name, config_entry.owner, config_entry.url)

    def add_row(self, name: str, owner: str, url: str) -> None:
        super().add_row(name, owner, url)
