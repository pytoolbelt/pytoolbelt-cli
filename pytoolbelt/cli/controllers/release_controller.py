from pytoolbelt.core.project.toolbelt_components import ToolbeltPaths
from pytoolbelt.core.project.tool_components import ToolPaths, ToolConfig
from pytoolbelt.core.data_classes.component_metadata import ComponentMetadata
from pytoolbelt.core.project.ptvenv_components import PtVenvPaths, PtVenvConfig
from pytoolbelt.core.tools.git_client import GitClient
from pytoolbelt.core.data_classes.pytoolbelt_config import PytoolbeltConfig, pytoolbelt_config


class ReleaseController:

    def __init__(self) -> None:
        self.toolbelt_paths = ToolbeltPaths()

    @pytoolbelt_config
    def release(self, ptc: PytoolbeltConfig) -> int:

        git_client = GitClient.from_path(path=self.toolbelt_paths.root_path, release_branch=ptc.release_branch)

        print("Fetching remote tags...")
        git_client.fetch_remote_tags()

        print("checking git release requirements...")
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
            print("No new releases to make. Exiting.")
            return 0

        for release in releases:
            print(f"tagging release {release.release_tag}...")
            git_client.tag_release(release.release_tag)

        print("Pushing tags to remote...")
        git_client.push_tags_to_remote()
        return 0
