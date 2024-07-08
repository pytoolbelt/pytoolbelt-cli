from pathlib import Path
from typing import Optional, Union
from pytoolbelt.core.project.toolbelt_components import ToolbeltPaths, ToolbeltTemplater
from pytoolbelt.core.project.tool_components import ToolPaths
from pytoolbelt.core.project.ptvenv_components import PtVenvPaths
from pytoolbelt.core.tools.git_client import GitClient
from pytoolbelt.core.data_classes.pytoolbelt_config import PytoolbeltConfig


class Project:
    def __init__(self, root_path: Optional[Path] = None, **kwargs) -> None:
        self.paths = kwargs.get("paths", ToolbeltPaths(toolbelt_root=root_path))
        self.templater = kwargs.get("templater", ToolbeltTemplater(self.paths))

    def create(self, overwrite: Optional[bool] = False) -> None:
        self.paths.create()
        self.templater.template_new_toolbelt_files(overwrite)
        GitClient.init_if_not_exists(self.paths.toolbelt_dir)

    def release(self, ptc: PytoolbeltConfig, component_paths: Union[PtVenvPaths, ToolPaths]) -> int:

        if isinstance(component_paths, PtVenvPaths):
            kind = "ptvenv"
        elif isinstance(component_paths, ToolPaths):
            kind = "tool"
        else:
            raise ValueError("Invalid component paths passed to release method.")

        git_client = GitClient.from_path(path=self.paths.root_path, release_branch=ptc.release_branch)

        # first fetch all remote tags if we don't have them
        print("Fetching remote tags...")
        git_client.fetch_remote_tags()

        # run all the checks to ensure we can release
        print("checking git release requirements...")
        git_client.raise_on_release_attempt()

        try:
            release_tags = getattr(git_client, f"{kind}_releases")(as_names=True)
        except AttributeError:
            raise ValueError("Invalid kind passed to release method.")

        if component_paths.meta.release_tag in release_tags:
            print(f"Release tag {component_paths.meta.release_tag} already exists. Nothing to do.")
            return 0

        # otherwise release the component
        print("tagging release...")
        git_client.tag_release(component_paths.meta.release_tag)

        print("Pushing tags to remote...")
        git_client.push_tags_to_remote()
        return 0
