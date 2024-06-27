import os
from argparse import Namespace
from typing import Optional
from pathlib import Path
from pytoolbelt.environment.config import PYTOOLBELT_TOOLS_DIR


def add_path(cliargs: Namespace, directory: Optional[Path] = PYTOOLBELT_TOOLS_DIR):

    # Check if directory exists
    if not directory.exists():
        print(f"Directory {directory} does not exist.")
        return

    # Check if directory is already in PATH
    if directory.as_posix() in os.environ['PATH']:
        print(f"Directory {directory} is already in PATH.")
        return

    # Determine the shell and corresponding configuration file
    shell = os.environ['SHELL']
    if shell.endswith('bash'):
        shell_config_file = os.path.expanduser('~/.bash_profile')
    elif shell.endswith('zsh'):
        shell_config_file = os.path.expanduser('~/.zshrc')
    else:
        print(f"Unsupported shell: {shell}")
        return

    # Append export command to shell configuration file
    with open(shell_config_file, 'a') as file:
        file.write(f'\nexport PATH="$PATH:{directory}"\n')

    print(f"Directory {directory} added to PATH in {shell}. Please restart your shell or run `source {shell_config_file}` for the changes to take effect.")
