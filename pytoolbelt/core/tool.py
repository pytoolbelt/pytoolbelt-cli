from pytoolbelt.bases.basepaths import BasePaths
from pathlib import Path
from typing import Optional, List
from pytoolbelt.environment.variables import PYTOOLBELT_PROJECT_ROOT
from semver import Version


class ToolPaths(BasePaths):

    def __init__(self, name: str, root_path: Optional[Path], version: Optional[Version] = None) -> None:
        self._version = version or Version.parse("0.0.0")
        super().__init__(root_path=root_path or PYTOOLBELT_PROJECT_ROOT, name=name, kind="tool")

    @property
    def version(self) -> Version:
        return self._version

    @version.setter
    def version(self, version: Version) -> None:
        self._version = version

    @property
    def tools_root_dir(self) -> Path:
        return self.root_path / "tools"

    @property
    def tool_dir(self) -> Path:
        return self.tools_root_dir / self.name

    @property
    def new_directories(self) -> List[Path]:
        return [
            self.tools_root_dir,
            self.tool_dir
        ]

    @property
    def new_files(self) -> List[Path]:
        return []

    @property
    def release_tag(self) -> str:
        return f"{self.kind}-{self.name}-{str(self.version)}"
