from argparse import Namespace
from dataclasses import dataclass, fields


@dataclass
class BaseControllerParameters:
    action: str

    @classmethod
    def from_cliargs(cls, cliargs: Namespace) -> "BaseControllerParameters":
        kwargs = {}
        for field in fields(cls):
            kwargs[field.name] = getattr(cliargs, field.name, None)
        return cls(**kwargs)
