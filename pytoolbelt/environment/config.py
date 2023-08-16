from pathlib import Path

DEFAULT_PYTHON_VERSION = "3.11"
PYTOOBELT_HOST = "http://localhost:8000"

class ProjectTree:
    ROOT_DIRECTORY = Path("~/.pytoolbelt").expanduser()
    TOOLS_DIRECTORY = ROOT_DIRECTORY / "tools"
    ENVIRONMENTS_DIRECTORY = ROOT_DIRECTORY / "environments"
    ENVIRONMENTS_METADATA_DIRECTORY = ENVIRONMENTS_DIRECTORY / "metadata"
    BIN_DIRECTORY = ROOT_DIRECTORY / "bin"
    TEMP_DIRECTORY = ROOT_DIRECTORY / "temp"
