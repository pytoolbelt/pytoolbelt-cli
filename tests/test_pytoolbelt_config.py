from unittest.mock import MagicMock, patch

import pytest

from pytoolbelt.core.data_classes.pytoolbelt_config import (
    PytoolbeltConfig,
    PytoolbeltError,
    pytoolbelt_config,
)


class MockParams:

    def __init__(self):
        self.toolbelt = "mock_toolbelt"


def test_pytoolbelt_config_loads_with_valid_config(tmp_path):
    config_file = tmp_path / "pytoolbelt.yml"
    config_file.write_text(
        """
project-config:
  python: "3.8"
  bump: "patch"
  envfile: ".env"
  release_branch: "main"
"""
    )
    config = PytoolbeltConfig.load(tmp_path)
    assert config.python == "3.8"
    assert config.bump == "patch"
    assert config.envfile == ".env"
    assert config.release_branch == "main"


def test_pytoolbelt_config_raises_exception_when_file_missing(tmp_path):
    with pytest.raises(PytoolbeltError):
        PytoolbeltConfig.load(tmp_path)


def test_pytoolbelt_config_decorator_without_ptc():
    @pytoolbelt_config(provide_ptc=False)
    def sample_function(*args, **kwargs):
        return kwargs.get("ptc"), kwargs.get("toolbelt")

    toolbelt_mock = MagicMock()
    toolbelt_mock.path = "mock_path"

    with patch("pytoolbelt.core.data_classes.toolbelt_config.ToolbeltConfigs.load") as mock_load:
        mock_load.return_value.get.return_value = toolbelt_mock
        ptc, toolbelt = sample_function(params=MockParams())

    assert ptc is None
    assert toolbelt == toolbelt_mock


def test_pytoolbelt_config_decorator_with_ptc():
    @pytoolbelt_config(provide_ptc=True)
    def sample_function(*args, **kwargs):
        return kwargs.get("ptc"), kwargs.get("toolbelt")

    toolbelt_mock = MagicMock()
    toolbelt_mock.path = "mock_path"
    ptc_mock = PytoolbeltConfig(python="3.8", bump="patch", envfile=".env", release_branch="main")

    with (
        patch("pytoolbelt.core.data_classes.toolbelt_config.ToolbeltConfigs.load") as mock_load,
        patch("pytoolbelt.core.data_classes.pytoolbelt_config.PytoolbeltConfig.load") as mock_load_ptc,
    ):
        mock_load.return_value.get.return_value = toolbelt_mock
        mock_load_ptc.return_value = ptc_mock
        ptc, toolbelt = sample_function(params=MockParams())

    assert ptc == ptc_mock
    assert toolbelt == toolbelt_mock
