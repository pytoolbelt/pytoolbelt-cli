import shutil
import tempfile
from pathlib import Path
from typing import Optional

from semver import Version

from pytoolbelt.cli.views.tool_views import (
    ToolInstalledTableView,
    ToolReleasesTableView,
)
from pytoolbelt.core.data_classes.component_metadata import ComponentMetadata
from pytoolbelt.core.error_handling.exceptions import ToolCreationError
from pytoolbelt.core.prompts import exit_on_no
from pytoolbelt.core.tools.git_client import GitClient

from .ptvenv_components import PtVenvBuilder, PtVenvConfig, PtVenvPaths, PtVenvTemplater
from .tool_components import ToolConfig, ToolInstaller, ToolPaths, ToolTemplater
from .toolbelt_components import ToolbeltPaths, ToolbeltTemplater


class Tool:
    def __init__(self, meta: ComponentMetadata, root_path: Optional[Path] = None, **kwargs) -> None:
        self.project_paths = kwargs.get("project_paths", ToolbeltPaths(root_path))
        self.paths = kwargs.get("paths", ToolPaths(meta, self.project_paths))
        self.templater = kwargs.get("templater", ToolTemplater(self.paths))
        self.installer = kwargs.get("installer", ToolInstaller(self.paths))

    @classmethod
    def from_cli(
        cls,
        string: str,
        root_path: Optional[Path] = None,
        creation: Optional[bool] = False,
        release: Optional[bool] = False,
    ) -> "Tool":
        meta = ComponentMetadata.as_tool(string)
        inst = cls(meta, root_path)

        if creation:
            inst.paths.meta.version = Version.parse("0.0.1")
            return inst

        if release:
            # this means we are building, or releasing a new version,
            # and we passed in a version number in the format name==version
            if isinstance(meta.version, Version):
                return inst
            config = ToolConfig.from_file(inst.paths.tool_config_file)
            inst.paths.meta.version = config.version
            return inst

        return inst

    def raise_if_exists(self) -> None:
        if self.paths.tool_dir.exists():
            raise ToolCreationError(f"A tool named '{self.paths.meta.name}' already exists in this project.")

    def create(self) -> None:
        self.raise_if_exists()
        self.paths.create()
        self.templater.template_new_tool_files()

    def install(self, dev_mode: bool) -> None:
        tool_config = ToolConfig.from_file(self.paths.tool_config_file)
        ptvenv_paths = PtVenvPaths.from_tool_config(tool_config, self.project_paths)

        if not ptvenv_paths.install_dir.exists():
            exit_on_no(
                prompt_message=f"Python environment {ptvenv_paths.meta.name} version {ptvenv_paths.meta.version} is not installed. Install it now?",
                exit_message="Unable to install tool. Exiting.",
            )
            ptvenv = PtVenv.from_ptvenv_paths(ptvenv_paths)
            ptvenv.build(force=False)

        if dev_mode:
            self.installer.install_shim(ptvenv_paths.python_executable_path.as_posix())
        else:
            self.installer.install(ptvenv_paths.python_executable_path.as_posix())

    def installed(self) -> None:
        table = ToolInstalledTableView()
        installed_tools = list(self.project_paths.iter_installed_tools())
        installed_tools.sort(key=lambda x: (x.version, x.name), reverse=True)

        for installed_tool in installed_tools:
            tool_paths = ToolPaths(installed_tool, self.project_paths)
            table.add_row(installed_tool.name, installed_tool.version, tool_paths.display_install_path)
        table.print_table()

    def remove(self) -> None:
        if self.paths.install_path.exists():
            self.paths.install_path.unlink()
        else:
            raise ToolCreationError(f"Tool {self.paths.meta.name} does not exist.")

    def release(self) -> None:
        project = Project()
        project.release(self.paths)

    def releases(self) -> None:
        repo_config = self.project_paths.get_pytoolbelt_config().get_repo_config("default")
        table = ToolReleasesTableView(repo_config)
        git_client = GitClient.from_path(self.project_paths.root_path)

        for tag in git_client.tool_releases():
            meta = ComponentMetadata.from_release_tag(tag.name)
            table.add_row(meta.name, meta.version, str(tag.commit.committed_datetime.date()), tag.commit.hexsha)
        table.print_table()
