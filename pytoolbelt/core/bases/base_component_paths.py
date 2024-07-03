from pathlib import Path
from typing import List, Union

from semver import Version

from pytoolbelt.bases.base_paths import BasePaths
from pytoolbelt.core.data_classes.name_version import ComponentMeta
from pytoolbelt.environment.config import PYTOOLBELT_PROJECT_ROOT


class BaseComponentPaths(BasePaths):
    def __init__(self, name_version: ComponentMeta, kind: str, root_path: Optional[Path] = None) -> None:
        root_path = root_path or PYTOOLBELT_PROJECT_ROOT
        super().__init__(root_path=root_path, name=name_version.name, kind=kind)
        self._name_version = name_version

    @property
    def new_directories(self) -> List[Path]:
        return []

    @property
    def new_files(self) -> List[Path]:
        return []

    @property
    def version(self) -> Union[Version, str]:
        return self._name_version.version
