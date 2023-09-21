from pytoolbelt.bases import PyToolBeltCommand
from pytoolbelt.core.error_handlers import handle_cli_errors
from pytoolbelt.environment.variables import PYTOOLBELT_DEFAULT_PYTHON_VERSION
from pytoolbelt.core.pyenv import PyEnv
from pytoolbelt.core.tool import Tool as PYTBTool
from pytoolbelt.model_utils.pyenv import PyEnvModelFactory
from pytoolbelt.core.exceptions import CommandError

__version__ = "0.0.0"


class Version(PyToolBeltCommand):

    def __call__(self) -> None:
        print(f"PyToolBelt :: Version {__version__} :: A tool for installing and managing tools written in python.")


class Project(PyToolBeltCommand):
    args = {
        ("--init", "-i"): {
            "help": "Initialize a new project",
            "action": "store_true",
            "default": False
        }
    }

    @handle_cli_errors
    def __call__(self) -> int:
        if self.cli_args.init:
            return self.init()

    def init(self) -> int:
        creator = self.project.get_project_creator()
        creator.create()
        print("PyToolBelt :: Initialized pytoolbelt project!")
        return 0


class Pyenv(PyToolBeltCommand):
    args = {

        ("--new", "-n"): {
            "help": "Create a new environment definition",
            "default": None
        },

        ("--destroy", "-d"): {
            "help": "Destroy an environment definition",
            "default": None
        },

        ("--build", "-b"): {
            "help": "Build a venv",
        },

        ("--python-version",): {
            "help": "Python version to use for the venv",
            "default": PYTOOLBELT_DEFAULT_PYTHON_VERSION
        },

        ("--fetch", "-f"): {
            "help": "Fetch a venv from the index",
            "default": None
        },

        ("--publish", "-p"): {
            "default": None
        }
    }

    @handle_cli_errors
    def __call__(self) -> int:

        if self.cli_args.new:
            return self.new(self.cli_args.new, self.cli_args.python_version)

        if self.cli_args.destroy:
            return self.destroy(self.cli_args.destroy, self.cli_args.python_version)

        if self.cli_args.fetch:
            return self.fetch(self.cli_args.fetch)

        if self.cli_args.build:
            return self.build(self.cli_args.build)

        if self.cli_args.publish:
            return self.publish(self.cli_args.publish, self.cli_args.python_version)

    @staticmethod
    def new(name: str, python_version: str) -> int:
        pyenv = PyEnv(name, python_version)

        creator = pyenv.get_creator()
        creator.create()

        writer = pyenv.get_writer()
        writer.write()

        print(f"PyToolBelt :: Created environment metadata {name} for python version {python_version}")
        return 0

    @staticmethod
    def destroy(name: str, python_version: str) -> int:
        pyenv = PyEnv(name, python_version)

        destroyer = pyenv.get_destroyer()
        destroyer.destroy()

        print(f"PyToolBelt :: Destroyed environment metadata {name}")
        return 0

    @staticmethod
    def build(name: str) -> int:
        pyenv = PyEnv.from_name(name)

        builder = pyenv.get_builder()
        builder.build()

        paths = pyenv.get_paths()
        pyenv_model = PyEnvModelFactory.from_path(paths.pyenv_definition_file)

        print(f"PyToolBelt :: Built environment {name} for python version {pyenv_model.python_version}")
        return 0

    def fetch(self, pyenv_id: str) -> int:
        print(f"PyToolBelt :: Fetched environment {pyenv_id}")
        return 0

    def publish(self, name: str, python_version: str) -> int:
        print(f"PyToolBelt :: Published environment {name} for python version {python_version}")
        return 0


class Tool(PyToolBeltCommand):
    args = {
        ("--new", "-n"): {
            "help": "Create a new tool",
            "default": None
        },

        ("--zip", "-z"): {
            "help": "Create a zip file for a tool",
            "default": None
        },

        ("--clean", "-c"): {
            "help": "Clean up a tool's zip archives and packages",
            "default": None
        },

        ("--install", "-i"): {
            "help": "Build and install a tool. If the tool raise_if_exists locally, it will be installed, if not, the tools will be downloaded from www.pytoolbelt.com",
            "default": False
        },

        ("--editable", "-e"): {
            "help": "Install a tool in editable mode",
            "action": "store_true",
            "default": False
        },

        ("--quality", "-q"): {
            "help": "Run code quality checks on a tool",
            "default": None
        },

        ("--uninstall", "-u"): {
            "help": "Uninstall a tool from the project's bin directory, keeping the tool definition if it raise_if_exists",
            "default": None

        },

        ("--show", "-s"): {
            "help": "List all tools",
            "action": "store_true",
            "default": False
        },

        ("--publish", "-p"): {
            "help": "Upload a tool to a remote repository",
            "default": None
        },

        ("--test", "-t"): {
            "help": "Run pytest for a tool",
            "default": None
        }
    }

    @handle_cli_errors
    def __call__(self) -> int:

        self._validate_flags()

        if self.cli_args.new:
            return self.new(self.cli_args.new)

        if self.cli_args.zip:
            return self.zip(self.cli_args.zip)

        if self.cli_args.clean:
            return self.clean(self.cli_args.clean)

        if self.cli_args.install:
            return self.install(self.cli_args.install, self.cli_args.editable)

        if self.cli_args.quality:
            return self.quality(self.cli_args.quality)

    # if self.cli_args.install:
    #     return self.install(self.cli_args.install)
    #
    # if self.cli_args.remove:
    #     return self.remove(self.cli_args.remove)
    #
    # if self.cli_args.show:
    #     return self.show()
    #
    # if self.cli_args.publish:
    #     return self.publish(self.cli_args.publish)
    #
    # if self.cli_args.format:
    #     return self.format(self.cli_args.format)
    #
    # if self.cli_args.test:
    #     return self.test(self.cli_args.test)

    def _validate_flags(self) -> None:
        if self.cli_args.editable and not self.cli_args.install:
            raise CommandError("Cannot use --editable without --install")

    @staticmethod
    def new(name: str) -> int:
        tool = PYTBTool(name)

        creator = tool.get_creator()
        creator.create()

        writer = tool.get_writer()
        writer.write()
        print(f"PyToolBelt :: Created tool {name}.")
        return 0

    @staticmethod
    def zip(name: str) -> int:
        tool = PYTBTool(name)
        zipper = tool.get_zipper()
        zipper.zip()
        print(f"PyToolBelt :: Created zip archive for tool {name}")
        return 0

    @staticmethod
    def clean(name: str) -> int:
        tool = PYTBTool(name)
        cleaner = tool.get_cleaner()
        cleaner.clean()
        print(f"PyToolBelt :: Cleaned up zip archives for tool {name}")
        return 0

    @staticmethod
    def install(name: str, editable: bool) -> int:
        tool = PYTBTool(name)
        installer = tool.get_installer()
        installer.install(editable)
        return 0

    @staticmethod
    def uninstall(name: str) -> int:
        pass

    @staticmethod
    def quality(name: str) -> int:
        tool = PYTBTool(name)
        formatter = tool.get_formatter()
        formatter.format()
        return 0

    def remove(self, name: str) -> int:

        tool = self.project.new_tool(name)
        tool_builder = tool.get_builder()

        if tool_builder.executable_path.raise_if_exists():
            tool_builder.executable_path.unlink()

        print(f"PyToolBelt :: Removed tool {name} from {self.project.bin_path}")
        return 0

    def show(self) -> int:
        print("PyToolBelt :: Listing all tools")
        tool_info = self.project.get_tool_info()
        tool_info.display()
        return 0

    def publish(self, name: str) -> int:
        tool = self.project.new_tool(name)
        tool_publisher = tool.get_publisher()
        tool_publisher.publish()

        print(f"PyToolBelt :: Published tool {name} to remote repository")
        return 0

    def format(self, name: str) -> int:
        tool = self.project.new_tool(name)
        tool_formatter = tool.get_formatter()
        tool_formatter.format()

        print(f"PyToolBelt :: Formatted tool {name}")
        return 0

    def test(self, name: str) -> int:
        tool = self.project.new_tool(name)
        test_runner = tool.get_test_runner()
        test_runner.run()
        return 0
