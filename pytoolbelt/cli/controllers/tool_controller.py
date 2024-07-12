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

from pytoolbelt.core.error_handling.exceptions import CreateReleaseError
from pytoolbelt.core.project.tool_components import ToolPaths, ToolTemplater, ToolInstaller, ToolConfig
from pytoolbelt.core.project.toolbelt_components import ToolbeltPaths, ToolbeltConfigs
from pytoolbelt.core.data_classes.pytoolbelt_config import PytoolbeltConfig
from pytoolbelt.core.project.ptvenv_components import PtVenvPaths
from pytoolbelt.cli.controllers.ptvenv_controller import PtVenvController
from pytoolbelt.cli.controllers.common import release

"""
    TODO: This controller's constructors are quite similar to that of the tool controller. 
    this should be reviewed as a good candidate for DRY out refactoring.
"""


class ToolController:
    """Controller for managing tools."""
    def __init__(self, meta: ComponentMetadata, root_path: Optional[Path] = None, **kwargs) -> None:
        self.toolbelt_paths = kwargs.get("toolbelt_paths", ToolbeltPaths(root_path))
        self.paths = kwargs.get("paths", ToolPaths(meta, self.toolbelt_paths))
        self.templater = kwargs.get("templater", ToolTemplater(self.paths))
        self.installer = kwargs.get("installer", ToolInstaller(self.paths))

    @classmethod
    def for_creation(cls, string: str, root_path: Optional[Path] = None) -> "ToolController":
        version = Version.parse("0.0.1")
        meta = ComponentMetadata.as_tool(string, version)
        return cls(meta, root_path)

    @classmethod
    def for_deletion(cls, string: str, root_path: Optional[Path] = None) -> "ToolController":
        meta = ComponentMetadata.as_tool(string)
        return cls(meta, root_path)

    @classmethod
    def for_release(cls, string: str, root_path: Optional[Path] = None) -> "ToolController":
        meta = ComponentMetadata.as_tool(string)
        inst = cls(meta, root_path)

        # this means we passed in a version number, which should not be allowed.
        # Versions must always be bumped in the tool config file.
        if isinstance(meta.version, Version):
            raise CreateReleaseError(f"Cannot release tool {inst.paths.meta.name} with version {inst.paths.meta.version}. Versions must be bumped in the tool config file.")

        config = ToolConfig.from_file(inst.paths.tool_config_file)
        inst.paths.meta.version = config.version
        return inst

    @classmethod
    def for_installation(cls, string: str, root_path: Optional[Path] = None) -> "ToolController":
        meta = ComponentMetadata.as_tool(string)
        inst = cls(meta, root_path)

        # no version was passed in, so we are installing the latest version as declared in the tool config file
        if inst.paths.meta.is_latest_version:
            config = ToolConfig.from_file(inst.paths.tool_config_file)
            inst.paths.meta.version = config.version
            return inst
        # a version was passed in, so we are installing that specific version
        return inst

    def raise_if_exists(self) -> None:
        if self.paths.tool_dir.exists():
            raise ToolCreationError(f"A tool named '{self.paths.meta.name}' already exists in this project.")

    def raise_if_not_pytoolbelt_project(self) -> None:
        # TODO: This should be refactored to use the ToolbeltPaths class
        git_client = GitClient.from_path(self.toolbelt_paths.root_path)
        self.toolbelt_paths.raise_if_not_pytoolbelt_project(git_client.repo)

    def create(self) -> int:
        self.raise_if_not_pytoolbelt_project()
        self.raise_if_exists()
        self.paths.create()
        self.templater.template_new_tool_files()
        return 0

    def install(self, dev_mode: bool) -> int:
        tool_config = ToolConfig.from_file(self.paths.tool_config_file)
        ptvenv_paths = PtVenvPaths.from_tool_config(tool_config, self.toolbelt_paths)

        if not ptvenv_paths.install_dir.exists():
            exit_on_no(
                prompt_message=f"Python environment {ptvenv_paths.meta.name} version {ptvenv_paths.meta.version} is not installed. Install it now?",
                exit_message="Unable to install tool. Exiting.",
            )
            ptvenv = PtVenvController.from_ptvenv_paths(ptvenv_paths)
            ptvenv.build(force=False)

        if dev_mode:
            self.installer.install_shim(ptvenv_paths.python_executable_path.as_posix())
        else:
            self.installer.install(ptvenv_paths.python_executable_path.as_posix())
        return 0

    def installed(self) -> None:
        table = ToolInstalledTableView()
        installed_tools = list(self.toolbelt_paths.iter_installed_tools())
        installed_tools.sort(key=lambda x: (x.version, x.name), reverse=True)

        for installed_tool in installed_tools:
            tool_paths = ToolPaths(installed_tool, self.toolbelt_paths)
            table.add_row(installed_tool.name, installed_tool.version, tool_paths.display_install_path)
        table.print_table()

    def remove(self) -> None:
        if self.paths.install_path.exists():
            self.paths.install_path.unlink()
        else:
            raise ToolCreationError(f"Tool {self.paths.meta.name} does not exist.")

    def release(self, ptc: PytoolbeltConfig) -> int:
        return release(ptc=ptc, toolbelt_paths=self.toolbelt_paths, component_paths=self.paths)
