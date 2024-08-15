from unittest.mock import MagicMock, patch

import pytest
from semver import Version

from pytoolbelt.core.data_classes.component_metadata import ComponentMetadata
from pytoolbelt.core.project.ptvenv_components import PtVenvBuilder, PtVenvConfig, PtVenvPaths, PtVenvTemplater
from pytoolbelt.core.project.toolbelt_components import ToolbeltPaths


@pytest.fixture
def mock_toolbelt_paths():
    return MagicMock(spec=ToolbeltPaths)


@pytest.fixture
def mock_meta():
    return ComponentMetadata(name="mock_ptvenv", version=Version.parse("1.0.0"), kind="ptvenv")


@pytest.fixture
def mock_ptvenv_paths(mock_meta, mock_toolbelt_paths):
    return PtVenvPaths(meta=mock_meta, toolbelt_paths=mock_toolbelt_paths)


@pytest.fixture
def mock_ptvenv_config():
    return PtVenvConfig(name="mock_ptvenv", version=Version.parse("1.0.0"), python_version="3.10", requirements=["pytest"])


@pytest.fixture
def ptvenv_templater(mock_ptvenv_paths):
    return PtVenvTemplater(paths=mock_ptvenv_paths)


@pytest.fixture
def ptvenv_builder(mock_ptvenv_paths):
    return PtVenvBuilder(paths=mock_ptvenv_paths)


def test_ptvenv_config_from_file(mock_ptvenv_config, tmp_path):
    config_file = tmp_path / "mock_ptvenv.yml"
    config_file.write_text("""
    name: mock_ptvenv
    version: '1.0.0'
    python_version: '3.10'
    requirements:
      - pytest
    """)
    config = PtVenvConfig.from_file(config_file)
    assert config == mock_ptvenv_config


def test_ptvenv_config_to_dict(mock_ptvenv_config):
    config_dict = mock_ptvenv_config.to_dict()
    assert config_dict == {
        "name": "mock_ptvenv",
        "version": "1.0.0",
        "python_version": "3.10",
        "requirements": ["pytest"],
    }


@patch("shutil.copy")
def test_ptvenv_paths_copy_config_to_install_dir(mock_copy, mock_ptvenv_paths):
    mock_ptvenv_paths.copy_config_to_install_dir()
    mock_copy.assert_called_once()


@patch("yaml.dump")
def test_ptvenv_paths_write_to_config_file(mock_write_text, mock_ptvenv_paths, mock_ptvenv_config):
    mock_ptvenv_paths.write_to_config_file(mock_ptvenv_config)
    mock_write_text.assert_called_once()
