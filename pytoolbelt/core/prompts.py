from typing import Optional


def prompt_yes_no(message: str, default_yes: Optional[bool] = False) -> bool:

    if default_yes:
        return True

    while True:
        response = input(f"{message} (y/n): ").lower()
        if response == 'y':
            return True
        elif response == 'n':
            return False
        else:
            print("Invalid input. Please enter 'y' or 'n'.")
