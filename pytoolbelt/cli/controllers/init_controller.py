from pytoolbelt.environment.config import add_path, init_home


class InitController:
    @staticmethod
    def init_project(path: bool) -> int:
        init_home()
        print("Created .pytoolbelt home directory")

        if path:
            print("Adding .pytoolbelt/tools to $PATH")
            add_path()
        else:
            print(
                "To add .pytoolbelt/tools to $PATH, run `pytoolbelt init --path` "
                f"or add the following to your shell configuration file: export PATH=~/.pytoolbelt/tools:$PATH"
            )
        return 0
