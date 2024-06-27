from argparse import Action
from semver import Version
from typing import Union
from pytoolbelt.core.exceptions import CliArgumentError


class NameVersion:

    FORBIDDEN_NAME_CHARS = "!\"#$%&'()*+,-./:;<=>?@[\\]^`{|}~"

    def __init__(self, name: str, version: Union[Version, str]) -> None:
        self.name = name
        self._version = version or "latest"

    def __str__(self):
        return f"{self.name}-{self.version}"

    @classmethod
    def from_string(cls, string: str):
        name, sep, version = string.partition("==")

        if not sep:
            inst = cls(name, "latest")
            inst.raise_if_forbidden_char_in_name()
            return inst

        try:
            inst = cls(name, Version.parse(version))
            inst.raise_if_forbidden_char_in_name()
        except ValueError:
            raise CliArgumentError(f"Invalid Version :: {version} is not a valid version")

        return inst

    @property
    def version(self) -> Union[Version, str]:
        if isinstance(self._version, str):
            if self._version == "latest":
                return self._version
        return self._version

    def raise_if_forbidden_char_in_name(self) -> None:
        for char in self.name:
            if char in self.FORBIDDEN_NAME_CHARS:
                raise CliArgumentError(f"Invalid Name :: {char} is not allowed in name")


class ParseNameVersion(Action):

    def __call__(self, parser, namespace, values, option_string=None):
        name_versions = []
        for value in values:
            name_versions.append(NameVersion.from_string(value))
        setattr(namespace, self.dest, name_versions)
