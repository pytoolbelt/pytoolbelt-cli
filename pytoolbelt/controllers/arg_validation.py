from argparse import Action

FORBIDDEN_CHARS = "!\"#$%&'()*+,-./:;<=>?@[\\]^`{|}~"


def check_forbidden_chars(string: str) -> str:
    for char in string:
        if char in FORBIDDEN_CHARS:
            return char


class ValidateName(Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if char := check_forbidden_chars(values):
            print(f"ERROR :: Invalid Name :: {char} is not allowed in name")
            exit(1)
        setattr(namespace, self.dest, values)
