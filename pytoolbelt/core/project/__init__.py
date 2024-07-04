import shutil
import tempfile
from pathlib import Path
from typing import Optional, Union

from semver import Version

from pytoolbelt.core.data_classes.component_metadata import ComponentMetadata
from pytoolbelt.core.exceptions import (
    PtVenvCreationError,
    PtVenvNotFoundError,
    ToolCreationError,
)
from pytoolbelt.core.prompts import exit_on_no
from pytoolbelt.core.tools import hash_config
from pytoolbelt.core.tools.git_client import GitClient
# from pytoolbelt.core.tools.git_commands import GitCommands
from pytoolbelt.environment.config import PYTOOLBELT_PROJECT_ROOT
from pytoolbelt.views.ptvenv_views import PtVenvInstalledTableView

from .project_components import ProjectPaths, ProjectTemplater
from .ptvenv_components import PtVenvBuilder, PtVenvConfig, PtVenvPaths, PtVenvTemplater
from .tool_components import ToolConfig, ToolInstaller, ToolPaths, ToolTemplater


class Project:
    def __init__(self, root_path: Optional[Path] = None, **kwargs) -> None:
        self.paths = kwargs.get("paths", ProjectPaths(project_root=root_path))
        self.templater = kwargs.get("templater", ProjectTemplater(self.paths))

    def create(self, overwrite: Optional[bool] = False) -> None:
        self.paths.create()
        self.templater.template_new_project_files(overwrite)
        GitClient.init_if_not_exists(self.paths.project_dir)

    def release(self, component_paths: Union[PtVenvPaths, ToolPaths]) -> None:

        if isinstance(component_paths, PtVenvPaths):
            kind = "ptvenv"
        elif isinstance(component_paths, ToolPaths):
            kind = "tool"
        else:
            raise ValueError("Invalid component paths passed to release method.")

        repo_config = self.paths.get_pytoolbelt_config().get_repo_config("default")
        git_client = GitClient.from_path(self.paths.root_path, repo_config)

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
            return

        # otherwise release the component
        print("tagging release...")
        git_client.tag_release(component_paths.meta.release_tag)

        print("Pushing tags to remote...")
        git_client.push_tags_to_remote()


class PtVenv:
    def __init__(self, meta: ComponentMetadata, root_path: Optional[Path] = None, **kwargs) -> None:
        self.project_paths = kwargs.get("project_paths", ProjectPaths(root_path))
        self.paths = kwargs.get("paths", PtVenvPaths(meta, self.project_paths))
        self.templater = kwargs.get("templater", PtVenvTemplater(self.paths))
        self.builder = kwargs.get("builder", PtVenvBuilder(self.paths))

    @classmethod
    def from_ptvenv_paths(cls, paths: PtVenvPaths) -> "PtVenv":
        return cls(paths.meta, paths.project_paths, paths=paths)

    @classmethod
    def from_cli(
            cls,
            string: str,
            root_path: Optional[Path] = None,
            creation: Optional[bool] = False,
            deletion: Optional[bool] = False,
            build: Optional[bool] = False,
    ) -> "PtVenv":
        meta = ComponentMetadata.as_ptvenv(string)
        inst = cls(meta, root_path)

        # this means it's the first time we're creating a ptvenv definition file
        # for the passed in name. So we set the version to 0.0.1
        if creation:
            inst.paths.meta.version = Version.parse("0.0.1")
            return inst

        if deletion:
            if isinstance(inst.paths.meta.version, str):
                if inst.paths.meta.version == "latest":
                    latest_installed_version = inst.paths.get_latest_installed_version()
                    inst.paths.meta.version = latest_installed_version
                return inst

        if build:
            # this means we are building, or releasing a new version, and we passed in a version number in the format name==version
            if isinstance(meta.version, Version):
                return inst
            config = PtVenvConfig.from_file(inst.paths.ptvenv_config_file)
            inst.paths.meta.version = config.version
            return inst

        return inst

    @classmethod
    def from_release_tag(cls, tag: str, root_path: Optional[Path] = None) -> "PtVenv":
        meta = ComponentMetadata.from_release_tag(tag)
        return cls(meta, root_path)

    @property
    def release_tag(self) -> str:
        return self.paths.meta.release_tag

    def raise_if_exists(self) -> None:
        if self.paths.ptvenv_dir.exists():
            raise PtVenvCreationError(f"Python environment {self.paths.meta.name} already exists.")

    def create(self) -> None:
        self.raise_if_exists()
        self.paths.create()
        self.templater.template_new_venvdef_file()

    def build(self, force: bool, repo_config: str) -> None:
        kind = "ptvenv"
        ptvenv_config = PtVenvConfig.from_file(self.paths.ptvenv_config_file)

        # this means we passed in some version number in the format name==version
        # we need to get the current tags from the repo, if a suitable tag is found
        # we need to copy the entire repo to a temp dir, and check out the tag.
        # we can then install the environment from the temp dir, but we must construct new PtVenvPaths and a builder.
        if ptvenv_config.version != self.paths.meta.version:
            pytoolbelt_repo_config = self.project_paths.get_pytoolbelt_config().get_repo_config(repo_config)

            git_commands = GitCommands(pytoolbelt_repo_config)

            try:
                tag_reference = git_commands.get_local_tag(tag_name=self.paths.meta.release_tag, kind=kind)
            except ValueError:
                raise PtVenvCreationError(f"Version {self.paths.meta.version} not found in the repository.")

            with tempfile.TemporaryDirectory() as tmp_dir:
                tmp_path = Path(tmp_dir) / "pytoolbelt"

                # first thing to do is copy the repo over
                print(f"Copying {PYTOOLBELT_PROJECT_ROOT} to {tmp_path}")
                shutil.copytree(src=PYTOOLBELT_PROJECT_ROOT, dst=tmp_path)

                # get the git commands pointed at the temp repo
                tmp_git_commands = GitCommands(pytoolbelt_repo_config, root_path=tmp_path)

                # check out the tag in the temp repo
                print(f"Checking out tag {tag_reference}")
                tmp_git_commands.checkout_tag(tag_reference)

                # create new paths and builder
                tmp_project_paths = ProjectPaths(tmp_path)
                tmp_paths = PtVenvPaths(self.paths.meta, tmp_project_paths)
                tmp_ptvenv_config = PtVenvConfig.from_file(tmp_paths.ptvenv_config_file)

                if not self._installation_can_proceed(tmp_ptvenv_config):
                    if not force:
                        return

                tmp_builder = PtVenvBuilder(tmp_paths)
                print(f"Building {self.paths.meta.name} version {self.paths.meta.version} from {tag_reference}")
                tmp_builder.build()
                return

        else:
            if not self._installation_can_proceed(ptvenv_config):
                if not force:
                    return
            self.builder.build()

    def _installation_can_proceed(self, current_config: PtVenvConfig) -> bool:
        # the installation directory exists, so we need to check if the configuration has changed
        # if it has, we need to warn the user that the environment definition has changed, however
        # the version has not been updated. This could lead to unexpected behavior.
        if self.paths.install_dir.exists():

            installed_config = PtVenvConfig.from_file(self.paths.installed_config_file)

            hashed_current_config = hash_config(current_config)
            hashed_installed_config = hash_config(installed_config)

            installed_hash = self.paths.installed_hash_file.read_text()

            # this means that the installation file has been messed with, so we need to rebuild the environment
            if installed_hash != hashed_installed_config:
                raise PtVenvCreationError(
                    f"Warning 1: ptvenv definition for {self.paths.meta.name} version {self.paths.meta.version} has been modified since install. "
                    f"Please run 'ptvenv build --force' to rebuild the environment. This will replace {self.paths.meta.name} version {self.paths.meta.version} with the new version definition."
                )

            if hashed_current_config != hashed_installed_config:
                raise PtVenvCreationError(
                    f"Warning 2: ptvenv definition for {self.paths.meta.name} version {self.paths.meta.version} has changed since install. "
                    f"Please run 'ptvenv build --force' to rebuild the environment. This will replace {self.paths.meta.name} version {self.paths.meta.version} with the new version definition."
                )

            if hashed_current_config == hashed_installed_config:
                print(
                    f"Python environment {self.paths.meta.name} version {self.paths.meta.version} is already up to date."
                )
                return False
        return True

    def delete(self, _all: bool) -> None:
        if self.paths.install_dir.exists():
            if _all:
                shutil.rmtree(self.paths.install_root_dir)
            else:
                shutil.rmtree(self.paths.install_dir.parent)
        else:
            raise PtVenvNotFoundError(
                f"Python environment {self.paths.meta.name} version {self.paths.meta.version} is not installed."
            )

    def bump(self, part: str) -> None:
        config = PtVenvConfig.from_file(self.paths.ptvenv_config_file)
        next_version = self.paths.meta.version.next_version(part)
        config.version = str(next_version)
        self.paths.write_to_config_file(config)

    def release(self) -> None:
        project = Project()
        project.release(self.paths)

    def releases(self, repo_config_name: str) -> None:
        pytoolbelt_config = self.project_paths.get_pytoolbelt_config()
        repo_config = pytoolbelt_config.get_repo_config(repo_config_name)

        git_commands = GitCommands(repo_config)

        # get the local tags and pack them up into a dictionary as well
        for tag in git_commands.get_local_tags("ptvenv"):
            if self.paths.meta.name:
                if self.paths.meta.name in tag.name:
                    print(tag.name)
            else:
                print(tag.name)

    def installed(self) -> None:
        table = PtVenvInstalledTableView()
        installed_ptvenvs = list(self.project_paths.iter_installed_ptvenvs())
        installed_ptvenvs.sort(key=lambda x: (x.version, x.name), reverse=True)
        for installed_ptvenv in installed_ptvenvs:
            table.add_row(installed_ptvenv.name, installed_ptvenv.version)
        table.print_table()

    def fetch(self, repo_config_name: str, keep: bool, build: bool, force: bool) -> None:

        if not keep and not build:
            print("the ptvenv must be either kept with --keep, or built with --build or both, but not none")
            return

        if not build and force:
            print("the --force flag is only valid when building the ptvenv")
            return

        if keep:
            self.raise_if_exists()

        repo_config = self.project_paths.get_pytoolbelt_config().get_repo_config(repo_config_name)

        with tempfile.TemporaryDirectory() as tmpdir:
            print("setting up temp dir...")
            tmpdir_path = Path(tmpdir)

            print("cloning repo...")
            tmp_repo, tmp_repo_path = GitCommands.clone_repo_to_temp_dir(repo_config.url, tmpdir_path.as_posix())
            tmp_git_commands = GitCommands.from_repo(tmp_repo, repo_config)

            if isinstance(self.paths.meta.version, str) and self.paths.meta.version == "latest":
                print("latest version being fetched....")
                local_tags = tmp_git_commands.get_local_tags(kind="ptvenv", as_names=True)
                component_meta = [ComponentMetadata.from_release_tag(tag) for tag in local_tags if self.paths.meta.name in tag]
                component_meta.sort(key=lambda x: x.version, reverse=True)
                latest_meta = component_meta[0]
                tag = tmp_git_commands.get_local_tag(latest_meta.release_tag, kind="ptvenv")

            # otherwise we got a version passed in the cli so just assume it exists and check it out and if not... poop.
            else:
                print("passed in version being fetched.")
                tag = tmp_git_commands.get_local_tag(self.paths.meta.release_tag, kind="ptvenv")

            tmp_git_commands.checkout_tag(tag)
            tmp_project_paths = ProjectPaths(tmp_repo_path)
            tmp_ptvenv_paths = PtVenvPaths(self.paths.meta, tmp_project_paths)

            self.paths.ptvenv_dir.mkdir(parents=True, exist_ok=True)

            # we should only do this when we keep...
            shutil.copytree(tmp_ptvenv_paths.ptvenv_dir, self.paths.ptvenv_dir, dirs_exist_ok=True)

            if build:
                builder = PtVenvBuilder(tmp_ptvenv_paths)
                builder.build()

            # TODO: you need to fix this. gets deleted if already exists.... not good.
            if keep:
                if not self.paths.ptvenv_dir.exists():
                    shutil.rmtree(self.paths.ptvenv_dir)




class Tool:
    def __init__(self, meta: ComponentMetadata, root_path: Optional[Path] = None, **kwargs) -> None:
        self.project_paths = kwargs.get("project_paths", ProjectPaths(root_path))
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
            # this means we are building, or releasing a new version, and we passed in a version number in the format name==version
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

    def install(self, repo_config: str) -> None:
        tool_config = ToolConfig.from_file(self.paths.tool_config_file)
        ptvenv_paths = PtVenvPaths.from_tool_config(tool_config, self.project_paths)

        if not ptvenv_paths.install_dir.exists():
            exit_on_no(
                f"Python environment {ptvenv_paths.meta.name} version {ptvenv_paths.meta.version} is not installed. Install it now?",
                "Unable to install tool. Exiting.",
            )
            ptvenv = PtVenv.from_ptvenv_paths(ptvenv_paths)
            ptvenv.build(force=False, repo_config=repo_config)
        self.installer.install(ptvenv_paths.python_executable_path.as_posix())

    def remove(self) -> None:
        if self.paths.install_path.exists():
            self.paths.install_path.unlink()
        else:
            raise ToolCreationError(f"Tool {self.paths.meta.name} does not exist.")

    def release(self) -> None:
        project = Project()
        project.release(self.paths)
