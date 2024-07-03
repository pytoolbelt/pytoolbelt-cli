from typing import Optional


def prompt_yes_no(message: str, default_yes: Optional[bool] = False) -> bool:

    if default_yes:
        return True

    while True:
        response = input(f"{message} (y/n): ").lower()
        if response == "y":
            return True
        elif response == "n":
            return False
        else:
            print("Invalid input. Please enter 'y' or 'n'.")


def exit_on_no(prompt_message: str, exit_message: str, default_yes: Optional[bool] = False):
    if not prompt_yes_no(prompt_message, default_yes):
        print(exit_message)
        exit(0)
