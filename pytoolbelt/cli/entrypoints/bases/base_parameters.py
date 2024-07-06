from argparse import Namespace
from dataclasses import dataclass, fields


@dataclass
class BaseEntrypointParameters:
    action: str

    @classmethod
    def from_cliargs(cls, cliargs: Namespace) -> "BaseEntrypointParameters":
        kwargs = {}
        for field in fields(cls):
            kwargs[field.name] = getattr(cliargs, field.name, None)
        return cls(**kwargs)
