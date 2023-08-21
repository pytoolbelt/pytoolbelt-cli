import zipapp
from pytoolbelt.core.tool import Tool
from pytoolbelt.core.pyenv import PyEnv


class Installer:

    def __init__(self, tool: Tool) -> None:
        self.tool = tool
        self.tool_metadata = None
        self.pyenv = None
        self.pyenv_metadata = None

    def install(self) -> None:

        if not self._tool_exists_locally():
            self._download_tool()
            self._unpack_tool()

        self._set_metadata()
        self._set_pyenv()
        self._set_pyenv_metadata()

        if not self._pyenv_exists_locally():
            self._download_pyenv()
            self._build_pyenv()

        self._build_tool()

    def _build_tool(self) -> None:
        metadata_config = self.tool.get_metadata().get_metadata_config()
        metadata_config.load()

        zipapp.create_archive(
            source=self.tool.src_directory,
            target=self.tool.executable_path,
            interpreter=metadata_config.interpreter_path.as_posix(),
        )

    def _tool_exists_locally(self) -> bool:
        return self.tool.tool_root.exists()

    def _download_tool(self) -> None:
        tool_downloader = self.tool.get_downloader()
        tool_downloader.download()

    def _set_metadata(self) -> None:
        metadata_config = self.tool.get_metadata().get_metadata_config()
        metadata_config.load(missing_venv_ok=True)
        self.tool_metadata = metadata_config

    def _set_pyenv(self) -> None:
        pyenv = PyEnv(self.tool_metadata.interpreter, self.tool_metadata.python_version)
        self.pyenv = pyenv

    def _set_pyenv_metadata(self) -> None:
        self.pyenv_metadata = self.pyenv.get_metadata()

    def _pyenv_exists_locally(self) -> bool:
        return self.pyenv_metadata.interpreter_install_path.exists()

    def _download_pyenv(self) -> None:
        pyenv_downloader = self.pyenv.get_downloader()
        pyenv_downloader.download()

    def _build_pyenv(self) -> None:
        pyenv_builder = self.pyenv.get_builder()
        pyenv_builder.build()

    def _unpack_tool(self) -> None:
        tool_packager = self.tool.get_packager()
        tool_packager.unpack()

    def _clean_up(self) -> None:
        self.tool.get_packager().purge()
