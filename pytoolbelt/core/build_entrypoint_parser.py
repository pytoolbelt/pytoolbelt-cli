from typing import Any, Callable, Dict, Optional


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

        for action, options in actions.items():
            action_parser = root_subparsers.add_parser(action, help=options["help"])
            action_parser.set_defaults(func=entrypoint)

            if common_flags:
                for flag, kwargs in common_flags.items():
                    action_parser.add_argument(flag, **kwargs)

            if "flags" in options.keys():
                for flag, kwargs in options["flags"].items():
                    action_parser.add_argument(flag, **kwargs)
