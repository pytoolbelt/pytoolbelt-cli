import hashlib
import json
import shutil
import tempfile
from contextlib import contextmanager
from pathlib import Path
from typing import Any, Callable, Dict, Optional

from git import Repo
from pydantic import BaseModel


def hash_config(model: BaseModel) -> str:
    model_json = json.dumps(model.to_dict())
    model_bytes = model_json.encode("utf-8")
    hash_object = hashlib.sha256()
    hash_object.update(model_bytes)
    return hash_object.hexdigest()


def build_entrypoint_parsers(
    subparser: Any,
    name: str,
    root_help: str,
    entrypoint: Callable,
    actions: Optional[Dict] = None,
    common_flags: Optional[Dict] = None,
) -> None:
    root_parser = subparser.add_parser(name, help=root_help)

    if not actions:
        root_parser.set_defaults(func=entrypoint)

        if common_flags:
            for flag, kwargs in common_flags.items():
                root_parser.add_argument(flag, **kwargs)

    if actions:
        root_subparsers = root_parser.add_subparsers(dest="action")
        root_subparsers.required = True

        sorted_actions = sorted(actions.keys())

        for sorted_action in sorted_actions:
            options = actions[sorted_action]
            action_parser = root_subparsers.add_parser(sorted_action, help=options["help"])
            action_parser.set_defaults(func=entrypoint)

            if common_flags:
                for flag, kwargs in common_flags.items():
                    action_parser.add_argument(flag, **kwargs)

            if "flags" in options.keys():
                for flag, kwargs in options["flags"].items():
                    action_parser.add_argument(flag, **kwargs)
