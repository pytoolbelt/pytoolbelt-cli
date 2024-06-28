from semver import Version
from typing import Union
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
            inst = cls(name, Version.parse(version))
            inst.raise_if_forbidden_char_in_name()
        except ValueError:
            raise CliArgumentError(f"Invalid Version :: {version} is not a valid version")

        return inst

    @classmethod
    def as_ptvenv(cls, string: str) -> "ComponentMetadata":
        return cls.from_string(string, "ptvenv")

    @classmethod
    def as_tool(cls, string: str) -> "ComponentMetadata":
        return cls.from_string(string, "tool")

    @classmethod
    def from_release_tag(cls, tag: str) -> "ComponentMetadata":
        kind, name, version = tag.split("-")
        inst = cls(name, version, kind)
        inst.raise_if_forbidden_char_in_name()
        return inst

    @property
    def version(self) -> Union[Version, str]:
        if isinstance(self._version, str):
            if self._version == "latest":
                return self._version
        return self._version

    @property
    def release_tag(self) -> str:
        return f"{self.kind}-{self.name}-{self.version}"

    def raise_if_forbidden_char_in_name(self) -> None:
        for char in self.name:
            if char in self.FORBIDDEN_NAME_CHARS:
                raise CliArgumentError(f"Invalid Name :: {char} is not allowed in name")
