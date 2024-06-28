import tempfile
from dataclasses import dataclass
from pytoolbelt.controllers.bases.base_parameters import BaseControllerParameters
from pytoolbelt.controllers.validation.name_validation import ParsePtVenvMeta
from pytoolbelt.core.data_classes.component_metadata import ComponentMetadata
from pytoolbelt.core.project import PtVenv
# from pytoolbelt.core.project.project import ProjectPaths
# from pytoolbelt.core.git_commands import GitCommands


@dataclass
class VenvDefControllerParameters(BaseControllerParameters):
    name: str
    repo_config: str
    all: bool


class VenvDefContext:
    def __init__(self, params: VenvDefControllerParameters) -> None:
        self.params = params


def new(context: VenvDefContext) -> int:
    ptvenv = PtVenv.from_cli(context.params.name, creation=True)
    ptvenv.create()
    return 0


def build(context: VenvDefContext) -> int:
    ptvenv = PtVenv.from_cli(context.params.name)
    ptvenv.build()
    return 0


def remove(context: VenvDefContext) -> int:
    ptvenv = PtVenv.from_cli(context.params.name)
    ptvenv.delete(context.params.all)
    return 0


# def release(context: VenvDefContext) -> int:
#     project_paths = ProjectPaths()
#     config = project_paths.get_pytoolbelt_config()
#     repo_config = config.get_repo_config(context.params.repo_config)
#
#     git_commands = GitCommands(repo_config)
#
#     # first fetch all remote tags if we don't have them
#     print("Fetching remote tags...")
#     git_commands.fetch_remote_tags()
#
#     # if we are not on the configured release branch, raise an error
#     # this will prevent tagging releases from non-release branches
#     print("Checking if we are on the release branch...")
#     git_commands.raise_if_not_release_branch()
#
#     # if we have uncommitted changes, raise an error. the local branch
#     # needs to be clean before tagging a release.
#     print("Checking for uncommitted changes...")
#     git_commands.raise_if_uncommitted_changes()
#
#     # if we have any untracked files, this would cause inconsistencies in the release tag
#     # and the files that have been added to the repo... so we raise an error here
#     print("Checking for untracked files...")
#     git_commands.raise_if_untracked_files()
#
#     # if the local release branch is behind the remote, raise an error
#     # which tells the user to pull the latest changes. This is to ensure
#     # that the changes in the release branch (likely master / main) have been merged
#     # into the release branch via PR before tagging a release.
#     print("Checking if the local and remote heads are the same...")
#     git_commands.raise_if_local_and_remote_head_are_different()
#
#     # get the local tags and pack them up into a dictionary as well
#     print("Getting local tags...")
#     local_tags = git_commands.get_local_tags()
#     local_tags = git_commands.group_versions(local_tags)
#
#     print("Getting ptvenv definitions to tag...")
#     ptvenv_defs_to_tag = project_paths.get_ptvenv_defs_to_tag(local_tags)
#
#     print("tagging ptvenv releases...")
#     for ptvenv_def in ptvenv_defs_to_tag:
#         print(f"Tagging {ptvenv_def.release_tag}...")
#         git_commands.tag_release(ptvenv_def.release_tag)
#
#     print("Pushing tags to remote...")
#     git_commands.push_all_tags_to_remote()
#     return 0
#
#
# def releases(context: VenvDefContext) -> int:
#     project_paths = ProjectPaths()
#     config = project_paths.get_pytoolbelt_config()
#     repo_config = config.get_repo_config(context.params.repo_config)
#
#     git_commands = GitCommands(repo_config)
#
#     # get the local tags and pack them up into a dictionary as well
#     local_tags = git_commands.get_local_tags()
#
#     for tag in local_tags:
#         if tag.name.startswith("ptvenv"):
#             print(tag.name)
#
#     return 0
#
#
# def fetch(context: VenvDefContext) -> int:
#     project_paths = ProjectPaths()
#     config = project_paths.get_pytoolbelt_config()
#     repo_config = config.get_repo_config(context.params.repo_config)
#
#     with tempfile.TemporaryDirectory() as tmp_repo:
#         repo, tmp_path = GitCommands.clone_repo_to_temp_dir(repo_config.url, tmp_repo)
#         git_commands = GitCommands.from_repo(repo, repo_config)
#
#         local_tags = git_commands.get_local_tags()
#         local_tags = git_commands.group_versions(local_tags, context.params.name)
#
#         # tags are already sorted by version number. so we can just grab the first one
#         # as long as it's not a prerelease version
#         target_version = None
#
#         if context.params.version == "latest":
#             for version in local_tags["ptvenv"][context.params.name]["versions"]:
#                 if not version.prerelease:
#                     target_version = version
#                     break
#         else:
#             target_version = vd.Version.parse(context.params.version)
#
#         tmp_vd_paths = vd.PtVenvPaths(root_path=tmp_path, name=context.params.name, version=target_version)
#         local_vd_paths = vd.PtVenvPaths(name=context.params.name, version=target_version)
#
#         # check out the tag before we read the contents of the venvdef file
#         git_commands.repo.git.checkout(local_vd_paths.release_tag)
#
#         tmp_content = tmp_vd_paths.venv_def_file.read_text()
#         local_vd_paths.venv_def_dir.mkdir(exist_ok=True, parents=True)
#         local_vd_paths.venv_def_file.touch(exist_ok=True)
#         local_vd_paths.venv_def_file.write_text(tmp_content)
#
#     return 0
#
#






COMMON_FLAGS = {}


ACTIONS = {
    "new": {
        "func": new,
        "help": "Create a new ptvenv definition file, or bump an existing one to a new version.",
        "flags": {
            "--name": {
                "help": "Name of the ptvenv definition to create",
                "required": True,
            }
        },

    },
    "build": {
        "func": build,
        "help": "Build a pytoolbelt ptvenv from a ptvenv definition yml file.",
        "flags": {
            "--name": {
                "help": "Name of the ptvenv to build.",
                "required": True,
            }
        },
    },
    "remove": {
        "func": remove,
        "help": "Remove a ptvenv definition from the local project.",
        "flags": {
            "--name": {
                "help": "Name of the ptvenv to remove. If no version provided, the most recent version will be removed.",
                "required": True,
            },
            "--all": {
                "help": "Remove all versions of the ptvenv definition.",
                "action": "store_true",
                "default": False,
            }
        },
    },
    # "releases": {
    #     "func": releases,
    #     "help": "List all ptvenv releases in the local git repository",
    # },
    # "fetch": {
    #     "func": fetch,
    #     "help": "Fetch a ptvenv release for a configured repository",
    #     "flags": {
    #         "--repo-config": {
    #             "help": "Repo name",
    #             "default": "default",
    #         },
    #
    #         "--version": {
    #             "help": "Version of the ptvenv release",
    #             "default": "latest",
    #         },
    #         "--name": {
    #             "help": "Name of the ptvenv definition to fetch",
    #             "required": True,
    #             "action": ParseNameVersion,
    #         }
    #     }
    # },
    # "release": {
    #     "func": release,
    #     "help": "deploy a ptvenv definition to a remote git repository",
    #     "flags": {
    #         "--repo-config": {
    #             "help": "Repo name",
    #             "default": "default",
    #         }
    #     }
    # },
}
