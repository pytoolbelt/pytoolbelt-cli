from pytoolbelt.bases import PyToolBeltCommand
from pytoolbelt.core.error_handlers import handle_cli_errors
from pytoolbelt.environment.config import DEFAULT_PYTHON_VERSION, STANDARD_PYENVS
from pytoolbelt.core.pyenv import PyEnv

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
        },

        ("--show", "-s"): {
            "help": "Show project configuration",
            "action": "store_true",
            "default": False
        }
    }

    @handle_cli_errors
    def __call__(self) -> int:

        if self.cli_args.init:
            return self.init()

        if self.cli_args.show:
            return self.show()

    def init(self) -> int:
        project_builder = self.project.get_project_builder()
        project_builder.build()
        print(f"PyToolBelt :: Initialized project at {self.project.cli_root}")
        return 0

    def show(self) -> int:
        project_info = self.project.get_project_info()
        project_info.display()
        return 0


class Pyenv(PyToolBeltCommand):
    args = {

        ("--new", "-n"): {
            "help": "Create a new environment definition",
            "default": None
        },

        ("--build", "-b"): {
            "help": "Build a venv",
        },

        ("--rebuild", "-r"): {
            "help": "Rebuild a venv",
        },

        ("--python-version", "-pv"): {
            "help": "Python version to use for the venv",
            "default": DEFAULT_PYTHON_VERSION
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

        if self.cli_args.fetch:
            return self.fetch(self.cli_args.fetch)

        if self.cli_args.build:
            return self.build(self.cli_args.build, self.cli_args.python_version)

        if self.cli_args.rebuild:
            return self.rebuild(self.cli_args.rebuild, self.cli_args.python_version)

        if self.cli_args.publish:
            return self.publish(self.cli_args.publish, self.cli_args.python_version)

    def new(self, name: str, python_version: str) -> int:
        pyenv = self.project.new_pyenv(name, python_version)

        metadata = pyenv.get_metadata()
        metadata.raise_if_exists()

        initializer = pyenv.get_initializer()
        initializer.initialize()

        templater = pyenv.get_templater()
        templater.template()

        print(f"PyToolBelt :: Created environment metadata {name} for python version {python_version}")
        return 0

    def build(self, name: str, python_version: str) -> int:
        pyenv = self.project.new_pyenv(name, python_version)

        initializer = pyenv.get_initializer()
        initializer.initialize()

        builder = pyenv.get_builder()
        builder.build()

        print(f"PyToolBelt :: Built environment {name} for python version {python_version}")
        return 0

    def fetch(self, pyenv_id: str) -> int:
        pyenv = self.project.new_pyenv_from_id(pyenv_id)
        pyenv_remote_manager = pyenv.get_pyenv_remote_manager()
        pyenv_remote_manager.download()

        print(f"PyToolBelt :: Fetched environment {pyenv_id}")
        return 0

    def rebuild(self, name: str, python_version: str) -> int:
        pyenv = self.project.new_pyenv(name, python_version)
        env_builder = pyenv.get_builder()
        env_builder.rebuild()

        print(f"PyToolBelt :: Rebuilt environment {name} for python version {python_version}")
        return 0

    def publish(self, name: str, python_version: str) -> int:
        pyenv = self.project.new_pyenv(name, python_version)
        pyenv_remote_manager = pyenv.get_pyenv_remote_manager()
        pyenv_remote_manager.upload()

        print(f"PyToolBelt :: Published environment {name} for python version {python_version}")
        return 0


class Tool(PyToolBeltCommand):
    args = {
        ("--new", "-n"): {
            "help": "Create a new tool",
            "default": None
        },

        ("--install", "-i"): {
            "help": "Build and install a tool. If the tool raise_if_exists locally, it will be installed, if not, the tools will be downloaded from www.pytoolbelt.com",
            "default": False
        },

        ("--remove", "-r"): {
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

        ("--format", "-f"): {
            "help": "Format a tool's code using black",
            "default": None
        },

        ("--test", "-t"): {
            "help": "Run pytest for a tool",
            "default": None
        }
    }

    @handle_cli_errors
    def __call__(self) -> int:

        if self.cli_args.new:
            return self.new(self.cli_args.new)

        if self.cli_args.install:
            return self.install(self.cli_args.install)

        if self.cli_args.remove:
            return self.remove(self.cli_args.remove)

        if self.cli_args.show:
            return self.show()

        if self.cli_args.publish:
            return self.publish(self.cli_args.publish)

        if self.cli_args.format:
            return self.format(self.cli_args.format)

        if self.cli_args.test:
            return self.test(self.cli_args.test)

    def new(self, name: str) -> int:
        tool = self.project.new_tool(name)
        metadata = tool.get_metadata()

        metadata.raise_if_exists()

        initializer = tool.get_initializer()
        initializer.initialize()

        tool_templater = tool.get_templater()
        tool_templater.template()

        print(f"PyToolBelt :: Created tool {name} at {metadata.tool_root}")
        return 0

    def install(self, name: str) -> int:
        tool = self.project.new_tool(name)
        installer = self.project.get_installer(tool)
        installer.install()
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
