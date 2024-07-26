from typing import Optional

from semver import Version

from pytoolbelt.cli.controllers.common import release
from pytoolbelt.core.data_classes.component_metadata import ComponentMetadata
from pytoolbelt.core.data_classes.pytoolbelt_config import PytoolbeltConfig
from pytoolbelt.core.data_classes.toolbelt_config import ToolbeltConfig
from pytoolbelt.core.error_handling.exceptions import PytoolbeltError, ToolCreationError
from pytoolbelt.core.project.ptvenv_components import PtVenvPaths
from pytoolbelt.core.project.tool_components import (
    ToolConfig,
    ToolInstaller,
    ToolPaths,
    ToolTemplater,
)
from pytoolbelt.core.project.toolbelt_components import ToolbeltPaths
from pytoolbelt.core.tools.git_client import TemporaryGitClient
from pytoolbelt.environment.config import get_logger

"""
    TODO: This controller's constructors are quite similar to that of the tool controller. 
    this should be reviewed as a good candidate for DRY out refactoring.
"""

logger = get_logger(__name__)


class ToolController:
    """Controller for managing tools."""

    def __init__(self, meta: ComponentMetadata, toolbelt: ToolbeltConfig, **kwargs) -> None:
        self.meta = meta
        self.toolbelt = toolbelt
        self.toolbelt_paths = kwargs.get("toolbelt_paths", ToolbeltPaths(toolbelt.path))
        self.tool_paths = kwargs.get("paths", ToolPaths(self.meta, self.toolbelt_paths))

    @classmethod
    def for_creation(cls, string: str, toolbelt: ToolbeltConfig) -> "ToolController":
        version = Version.parse("0.0.1")
        meta = ComponentMetadata.as_tool(string, version)
        logger.debug(f"Creating tool controller for_creation for {meta.name} with version {meta.version}.")
        return cls(meta, toolbelt)

    @classmethod
    def for_deletion(cls, string: str, toolbelt: ToolbeltConfig) -> "ToolController":
        meta = ComponentMetadata.as_tool(string)
        logger.debug(f"Creating tool controller for_deletion for {meta.name} with version {meta.version}.")
        return cls(meta, toolbelt)

    @classmethod
    def for_release(cls, string: str, toolbelt: ToolbeltConfig) -> "ToolController":
        meta = ComponentMetadata.as_tool(string)
        inst = cls(meta, toolbelt)

        # this means we passed in a version number, which should not be allowed.
        # Versions must always be bumped in the tool config file.
        if isinstance(meta.version, Version):
            raise PytoolbeltError(
                f"Cannot release tool {inst.meta.name} with version {inst.meta.version}. "
                f"Versions must be bumped in the tool config file."
            )

        config = ToolConfig.from_file(inst.tool_paths.tool_config_file)
        inst.meta.version = Version.parse(config.version)
        logger.debug(f"Creating tool controller for_release for {inst.meta.name} with version {inst.meta.version}.")
        return inst

    @classmethod
    def for_installation(cls, string: str, toolbelt: ToolbeltConfig) -> "ToolController":
        meta = ComponentMetadata.as_tool(string)
        inst = cls(meta, toolbelt)

        # no version was passed in, so we are installing the latest version as declared in the tool config file
        if inst.meta.is_latest_version:
            config = ToolConfig.from_file(inst.tool_paths.tool_config_file)
            inst.meta.version = config.version
            logger.debug(
                f"Creating tool controller for_installation for {inst.meta.name} with version {inst.meta.version}."
            )
            return inst

        # a version was passed in, so we are installing that specific version
        logger.debug(
            f"Creating tool controller for_installation for {inst.meta.name} with passed in version {inst.meta.version}."
        )
        return inst

    def get_templater(self) -> ToolTemplater:
        return ToolTemplater(self.tool_paths)

    def get_installer(self) -> ToolInstaller:
        return ToolInstaller(self.tool_paths)

    def create(self) -> int:
        self.toolbelt_paths.raise_if_not_pytoolbelt_project()
        self.tool_paths.raise_if_exists()
        self.tool_paths.create()
        self.get_templater().template_new_tool_files()
        logger.info(f"Tool {self.meta.name} created in toolbelt {self.toolbelt.name} at {self.tool_paths.tool_dir}.")
        return 0

    def _run_installer(self, p: PtVenvPaths, dev_mode: bool, installer: Optional[ToolInstaller] = None) -> int:
        installer = installer or self.get_installer()
        if dev_mode:
            logger.debug(f"Installing {self.meta.name} in dev mode.")
            return installer.install_shim(p.python_executable_path.as_posix())
        logger.debug(f"Installing {self.meta.name} in production mode.")
        return installer.install(p.python_executable_path.as_posix())

    def install(self, dev_mode: bool, from_config: bool) -> int:
        # TODO: This can be DRYed out. Check the build method of the PtVenvController.

        logger.info(f"Installing {self.meta.name} from toolbelt {self.toolbelt.name} at {self.tool_paths.tool_dir}.")

        with TemporaryGitClient(self.toolbelt.path, self.toolbelt.name) as (repo_path, git_client):
            logger.debug(f"toolbelt copied to temp dir: {repo_path.tmp_dir}")

            tool_config = ToolConfig.from_file(self.tool_paths.tool_config_file)

            ptvenv_paths = PtVenvPaths.from_tool_config(tool_config, self.toolbelt_paths)
            ptvenv_paths.raise_if_ptvenv_is_not_installed()

            if not from_config and not dev_mode:
                git_client.raise_if_uncommitted_changes()

            if from_config or dev_mode:
                return self._run_installer(ptvenv_paths, dev_mode)

            elif self.meta.is_latest_version:
                tags = git_client.tool_releases(name=self.meta.name, as_names=True)
                latest_meta = ComponentMetadata.get_latest_release(tags)

            else:
                latest_meta = self.meta

            try:
                tag_reference = git_client.get_tag_reference(latest_meta.release_tag)
            except IndexError:
                raise ToolCreationError(f"Tool {latest_meta.name} version {latest_meta.version} does not exist.")

            # check out from the release tag
            logger.debug(f"Checking out {latest_meta.release_tag}...")
            git_client.checkout_tag(tag_reference)

            # create new temp paths
            tmp_project_paths = ToolbeltPaths(repo_path.tmp_dir)
            tmp_paths = ToolPaths(latest_meta, tmp_project_paths)

            tmp_installer = ToolInstaller(tmp_paths)
            result = self._run_installer(ptvenv_paths, dev_mode, tmp_installer)
            logger.info(
                f"Tool {latest_meta.name} version {latest_meta.version} installed using ptvenv {ptvenv_paths.ptvenv_dir}."
            )

            return result

    def bump(self, ptc: PytoolbeltConfig, part: str) -> int:
        logger.info(f"Bumping version of tool {self.meta.name} in toolbelt {self.toolbelt.name}.")
        if part == "config":
            part = ptc.bump

        config = ToolConfig.from_file(self.tool_paths.tool_config_file)
        next_version = self.tool_paths.meta.version.next_version(part)
        config.version = next_version
        self.tool_paths.write_to_config_file(config)
        logger.info(f"Tool {self.meta.name} bumped to version {next_version}.")
        return 0

    def remove(self) -> int:
        logger.info(f"Removing tool {self.meta.name} from toolbelt {self.toolbelt.name}.")
        if self.tool_paths.install_path.exists():
            self.tool_paths.install_path.unlink()
        else:
            raise ToolCreationError(f"Tool {self.meta.name} does not exist.")
        logger.info(f"Tool {self.meta.name} removed.")
        return 0

    def release(self, ptc: PytoolbeltConfig) -> int:
        logger.info(f"Releasing tool {self.meta.name} version {self.meta.version} in toolbelt {self.toolbelt.name}.")
        return release(ptc=ptc, toolbelt_paths=self.toolbelt_paths, component_paths=self.tool_paths)
