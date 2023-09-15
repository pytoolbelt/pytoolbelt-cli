import zipapp
from pytoolbelt.core.tool import Tool
from pytoolbelt.core.pyenv import PyEnv


class Installer:

    def __init__(self, tool: Tool) -> None:
        self.tool = tool
        self.tool_metadata = self.tool.get_metadata()
        self.tool_metadata.load()

        self.pyenv = None
        self.pyenv_metadata = None

    def install(self) -> None:

        if not self._tool_exists_locally():
            self._download_tool()
            self._unpack_tool()

        self._set_pyenv()
        self._set_pyenv_metadata()

        if not self._pyenv_exists_locally():
            self._download_pyenv()
            self._build_pyenv()

        self._build_tool()

    def _build_tool(self) -> None:
        zipapp.create_archive(
            source=self.tool_metadata.src_directory,
            target=self.tool_metadata.executable_path,
            interpreter=self.tool_metadata.interpreter_path.as_posix(),
        )

    def _tool_exists_locally(self) -> bool:
        return self.tool_metadata.tool_root.exists()

    def _download_tool(self) -> None:
        pass

    def _set_pyenv(self) -> None:
        pyenv = PyEnv(self.tool_metadata.interpreter, self.tool_metadata.python_version)
        self.pyenv = pyenv

    def _set_pyenv_metadata(self) -> None:
        self.pyenv_metadata = self.pyenv.get_metadata()

    def _pyenv_exists_locally(self) -> bool:
        return self.pyenv_metadata.interpreter_install_path.exists()

    def _download_pyenv(self) -> None:
        pass

    def _build_pyenv(self) -> None:
        pyenv_builder = self.pyenv.get_builder()
        pyenv_builder.build()

    def _unpack_tool(self) -> None:
        tool_packager = self.tool.get_packager()
        tool_packager.unpack()

    def _clean_up(self) -> None:
        self.tool.get_packager().purge()
