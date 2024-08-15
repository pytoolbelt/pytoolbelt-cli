from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from pytoolbelt.core.data_classes.toolbelt_config import ToolbeltConfig
from pytoolbelt.core.error_handling.exceptions import PytoolbeltError
from pytoolbelt.core.project.toolbelt_components import ToolbeltPaths
from pytoolbelt.core.tools.formatting import BaseRuffFormatter, RuffFormatter, RuffInputSorter


@pytest.fixture
def mock_toolbelt_config():
    mock_config = MagicMock(spec=ToolbeltConfig)
    mock_config.path = Path("/fake/path")
    return mock_config


@pytest.fixture
def mock_toolbelt_paths(mock_toolbelt_config):
    return ToolbeltPaths(mock_toolbelt_config.path)


@patch("subprocess.Popen.communicate")
def test_base_ruff_formatter_run_success(mock_communicate, mock_toolbelt_config):
    mock_communicate.return_value = (b"output", b"")
    formatter = BaseRuffFormatter(mock_toolbelt_config, "ruff check .")
    formatter.returncode = 0
    formatter.run()
    mock_communicate.assert_called_once()


@patch("subprocess.Popen.communicate")
def test_base_ruff_formatter_run_failure(mock_communicate, mock_toolbelt_config):
    mock_communicate.return_value = (b"", b"error")
    formatter = BaseRuffFormatter(mock_toolbelt_config, "ruff check .")
    formatter.returncode = 1
    with pytest.raises(PytoolbeltError, match="Error while running ruff: error \(Exit code: 1\)"):
        formatter.run()
    mock_communicate.assert_called_once()


@patch("subprocess.Popen.__init__", return_value=None)
def test_ruff_formatter_init(mock_popen_init, mock_toolbelt_config):
    _ = RuffFormatter(mock_toolbelt_config)
    mock_popen_init.assert_called_once_with(args=["ruff", "format", str(mock_toolbelt_config.path / "tools")], stderr=-1, stdout=-1)


@patch("subprocess.Popen.__init__", return_value=None)
def test_ruff_input_sorter_init(mock_popen_init, mock_toolbelt_config):
    _ = RuffInputSorter(mock_toolbelt_config)
    mock_popen_init.assert_called_once_with(args=["ruff", "check", str(mock_toolbelt_config.path / "tools"), "--select", "I", "--fix"], stderr=-1, stdout=-1)
