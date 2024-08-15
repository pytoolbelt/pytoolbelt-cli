from pathlib import Path
from unittest.mock import mock_open, patch

import pytest

from pytoolbelt.core.data_classes.toolbelt_config import ToolbeltConfig, ToolbeltConfigs
from pytoolbelt.core.error_handling.exceptions import PytoolbeltError
from pytoolbelt.environment.config import PYTOOLBELT_TOOLBELT_INSTALL_DIR


@pytest.fixture
def mock_toolbelt_config():
    return ToolbeltConfig(url="git@github.com:owner/repo.git", owner="owner", name="repo", path=Path("/fake/path/repo"))


@pytest.fixture
def mock_toolbelt_configs(mock_toolbelt_config):
    return ToolbeltConfigs(repos={"repo": mock_toolbelt_config})


def test_toolbelt_config_from_url():
    config = ToolbeltConfig.from_url("git@github.com:owner/repo.git")
    assert config.url == "git@github.com:owner/repo.git"
    assert config.owner == "owner"
    assert config.name == "repo"
    assert config.path == PYTOOLBELT_TOOLBELT_INSTALL_DIR / "repo"


def test_toolbelt_config_to_dict(mock_toolbelt_config):
    config_dict = mock_toolbelt_config.to_dict()
    assert config_dict == {
        "url": "git@github.com:owner/repo.git",
        "owner": "owner",
        "name": "repo",
        "release_branch": "main",
        "path": "/fake/path/repo",
    }


@patch("builtins.open", new_callable=mock_open, read_data="repos: {}")
@patch("os.path.expandvars", side_effect=lambda x: x)
def test_toolbelt_configs_load(mock_expandvars, mock_file):
    with patch("pathlib.Path.open", mock_file):
        configs = ToolbeltConfigs.load()
        assert configs.repos == {}


def test_toolbelt_configs_get(mock_toolbelt_configs):
    config = mock_toolbelt_configs.get("repo")
    assert config.name == "repo"
    with pytest.raises(PytoolbeltError):
        mock_toolbelt_configs.get("nonexistent_repo")


@patch("builtins.open", new_callable=mock_open)
def test_toolbelt_configs_save(mock_file, mock_toolbelt_configs):
    with patch("pathlib.Path.open", mock_file):
        mock_toolbelt_configs.save()
        mock_file().write.assert_called()
