from pytoolbelt.controllers.parameters import ControllerParameters
from pytoolbelt.controllers.arg_validation import ValidateName
from pytoolbelt.core.git_commands import GitCommands
from pytoolbelt.core import tool
from pytoolbelt.core.ptvenv import PtVenvPaths
from semver import Version
from pytoolbelt.core.project import ProjectPaths
from dataclasses import dataclass
import tempfile
from pathlib import Path
from pytoolbelt.core.ptvenv import PtVenvPaths


@dataclass
class ToolControllerParameters(ControllerParameters):
    repo_config: str


class ToolContext:
    def __init__(self, params: ToolControllerParameters) -> None:
        self.params = params


def new(context: ToolContext) -> int:
    tp = tool.ToolPaths(context.params.name)
    tp.create()

    templater = tool.ToolTemplater(tp)
    templater.template_new_tool_files()
    return 0


def install(context: ToolContext) -> int:
    tp = tool.ToolPaths(context.params.name)
    tool_config = tp.get_tool_config()
    ptvenv_paths = PtVenvPaths(
        name=tool_config.ptvenv.name,
        version=Version.parse(tool_config.ptvenv.version)
    )

    tool_installer = tool.ToolInstaller(tp)
    tool_installer.install(ptvenv_paths.executable_path.as_posix())

    return 0


def release(context: ToolContext) -> int:
    project_paths = ProjectPaths()
    config = project_paths.get_pytoolbelt_config()
    repo_config = config.get_repo_config(context.params.repo_config)

    git_commands = GitCommands(repo_config)

    print("Fetching remote tags...")
    git_commands.fetch_remote_tags()

    print("Checking if we are on the release branch...")
    git_commands.raise_if_not_release_branch()

    print("Checking for uncommitted changes...")
    git_commands.raise_if_uncommitted_changes()

    print("Checking for untracked files...")
    git_commands.raise_if_untracked_files()

    print("Checking if the local and remote heads are the same...")
    git_commands.raise_if_local_and_remote_head_are_different()

    print("Getting local tags...")
    local_tags = git_commands.get_local_tags()
    local_tags = git_commands.group_versions(local_tags)

    tools_to_tag = project_paths.get_tools_to_tag(local_tags)

    for tool_to_tag in tools_to_tag:
        print(f"Tagging {tool_to_tag.release_tag}...")
        git_commands.tag_release(tool_to_tag.release_tag)

    print("Pushing tags to remote...")
    git_commands.push_all_tags_to_remote()

    return 0


def fetch(context: ToolContext) -> int:
    project_paths = ProjectPaths()
    config = project_paths.get_pytoolbelt_config()
    repo_config = config.get_repo_config(context.params.repo_config)

    git_commands = GitCommands(repo_config)

    print("Fetching remote tags...")
    git_commands.fetch_remote_tags()

    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_repo, tmp_path = git_commands.clone_repo_to_temp_dir(repo_config.url, tmpdir)
        git_commands = GitCommands.from_repo(tmp_repo, repo_config)

        local_tags = git_commands.get_local_tags()
        local_tags = git_commands.group_versions(local_tags)

        target_version = None

        if context.params.version == "latest":
            for version in local_tags["tool"][context.params.name]["versions"]:
                if not version.prerelease:
                    target_version = version
                    break
        else:
            target_version = Version.parse(context.params.version)

        tmp_tool_paths = tool.ToolPaths(root_path=Path(tmpdir), name=context.params.name, version=target_version)
        tool_config = tmp_tool_paths.get_tool_config()

        local_ptvenv_paths = PtVenvPaths(name=tool_config.ptvenv.name, version=Version.parse(tool_config.ptvenv.version))

        git_commands.repo.git.checkout(tmp_tool_paths.release_tag)

        tool_installer = tool.ToolInstaller(tmp_tool_paths)
        tool_installer.install(local_ptvenv_paths.executable_path.as_posix())

    return 0

COMMON_FLAGS = {}

ACTIONS = {
    "new": {
        "func": new,
        "help": "Create a new tool",
        "flags": {
            "--name": {
                "help": "Name of the tool",
                "required": True,
                "action": ValidateName,
            }
        }
    },
    "install": {
        "func": install,
        "help": "Install the tool",
        "flags": {
            "--name": {
                "help": "Name of the tool",
                "required": True,
                "action": ValidateName,
            }
        }
    },
    "release": {
        "func": release,
        "help": "Release the tool",
        "flags": {
            "--repo-config": {
                "help": "Name of the repo config",
                "action": ValidateName,
            },
            "--name": {
                "help": "Name of the tool",
                "required": True,
                "action": ValidateName,
            }
        },
    },
    "fetch": {
        "func": fetch,
        "help": "Fetch the tool",
        "flags": {
            "--repo-config": {
                "help": "Name of the repo config",
                "action": ValidateName,
            },
            "--name": {
                "help": "Name of the tool",
                "required": True,
                "action": ValidateName,
            },
            "--version": {
                "help": "Version of the tool",
                "default": "latest",
            }
        }
    }
}
