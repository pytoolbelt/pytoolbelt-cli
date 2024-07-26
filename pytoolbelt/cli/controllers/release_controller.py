from dataclasses import dataclass
from pathlib import Path

from pytoolbelt.cli.entrypoints.bases.base_parameters import BaseEntrypointParameters
from pytoolbelt.core.data_classes.component_metadata import ComponentMetadata
from pytoolbelt.core.data_classes.pytoolbelt_config import (
    PytoolbeltConfig,
    pytoolbelt_config,
)
from pytoolbelt.core.data_classes.toolbelt_config import ToolbeltConfig
from pytoolbelt.core.project.ptvenv_components import PtVenvConfig, PtVenvPaths
from pytoolbelt.core.project.tool_components import ToolConfig, ToolPaths
from pytoolbelt.core.project.toolbelt_components import ToolbeltPaths
from pytoolbelt.core.tools.git_client import GitClient
from pytoolbelt.environment.config import get_logger

logger = get_logger(__name__)


@dataclass
class ReleaseParameters(BaseEntrypointParameters):
    toolbelt: str


class ReleaseController:
    def __init__(self) -> None:
        self.toolbelt_paths = ToolbeltPaths()

    @pytoolbelt_config(provide_ptc=True)
    def release(self, ptc: PytoolbeltConfig, toolbelt: ToolbeltConfig, params: ReleaseParameters) -> int:

        git_client = GitClient.from_path(path=self.toolbelt_paths.root_path, release_branch=ptc.release_branch)

        logger.info("Fetching remote tags...")
        git_client.fetch_remote_tags()

        logger.info("checking git release requirements...")
        git_client.raise_on_release_attempt()

        component_versions = []
        for tool in self.toolbelt_paths.iter_tools():
            meta = ComponentMetadata.as_tool(tool)
            tool_paths = ToolPaths(meta, self.toolbelt_paths)
            tool_config = ToolConfig.from_file(tool_paths.tool_config_file)
            tool_paths.meta.version = tool_config.version
            component_versions.append(tool_paths.meta)

        for ptvenv in self.toolbelt_paths.iter_ptvenvs():
            meta = ComponentMetadata.as_ptvenv(ptvenv)
            ptvenv_paths = PtVenvPaths(meta, self.toolbelt_paths)
            ptvenv_config = PtVenvConfig.from_file(ptvenv_paths.ptvenv_config_file)
            ptvenv_paths.meta.version = ptvenv_config.version
            component_versions.append(ptvenv_paths.meta)

        release_tags = []
        release_tags.extend(git_client.tool_releases(as_names=True))
        release_tags.extend(git_client.ptvenv_releases(as_names=True))

        releases = []
        for component_version in component_versions:
            if component_version.release_tag not in release_tags:
                releases.append(component_version)

        if not releases:
            logger.info(f"No new releases to make in toolbelt {self.toolbelt_paths.toolbelt_dir.name}.")
            return 0

        for release in releases:
            logger.info(f"tagging release {release.release_tag}...")
            git_client.tag_release(release.release_tag)

        logger.info("Pushing tags to remote...")
        git_client.push_tags_to_remote()
        return 0


COMMON_FLAGS = {
    "--toolbelt": {"required": False, "help": "The help for toolbelt", "default": Path.cwd().name},
}
