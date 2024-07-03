from pathlib import Path
from typing import Optional, Union

from semver import Version

from pytoolbelt.core.exceptions import CliArgumentError


class ComponentMetadata:

    FORBIDDEN_NAME_CHARS = "!\"#$%&'()*+,-./:;<=>?@[\\]^`{|}~"

    def __init__(self, name: str, version: Union[Version, str], kind: str) -> None:
        self.name = name
        self.kind = kind
        self._version = version or "latest"

    def __str__(self) -> str:
        return self.release_tag

    @classmethod
    def from_string(cls, string: str, kind: str) -> "ComponentMetadata":
        name, sep, version = string.partition("==")

        if not sep:
            inst = cls(name, "latest", kind)
            inst.raise_if_forbidden_char_in_name()
            return inst

        try:
            inst = cls(name, Version.parse(version), kind)
            inst.raise_if_forbidden_char_in_name()
        except ValueError:
            raise CliArgumentError(f"Invalid Version :: {version} is not a valid version")

        return inst

    @classmethod
    def as_ptvenv(cls, string: str, version: Optional[Version] = None) -> "ComponentMetadata":
        inst = cls.from_string(string, "ptvenv")
        if version:
            inst.version = version
        return inst

    @classmethod
    def from_ptvenv_install_path(cls, path: Path) -> "ComponentMetadata":
        version = Version.parse(path.parent.name)
        name = path.parent.parent.name
        return cls(name, version, "ptvenv")

    @classmethod
    def as_tool(cls, string: str) -> "ComponentMetadata":
        return cls.from_string(string, "tool")

    @classmethod
    def from_release_tag(cls, tag: str) -> "ComponentMetadata":
        kind, name, version = tag.split("-", 2)
        inst = cls(name, version, kind)
        inst.raise_if_forbidden_char_in_name()
        return inst

    @property
    def version(self) -> Union[Version, str]:
        if isinstance(self._version, str):
            if self._version == "latest":
                return self._version
        return self._version

    @version.setter
    def version(self, value: Union[Version, str]) -> None:
        self._version = value

    @property
    def release_tag(self) -> str:
        return f"{self.kind}-{self.name}-{self.version}"

    def raise_if_forbidden_char_in_name(self) -> None:
        for char in self.name:
            if char in self.FORBIDDEN_NAME_CHARS:
                raise CliArgumentError(f"Invalid Name :: {char} is not allowed in name")
