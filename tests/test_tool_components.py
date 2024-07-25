from pathlib import Path
from unittest.mock import MagicMock, mock_open, patch

import pytest

from pytoolbelt.core.data_classes.component_metadata import ComponentMetadata
from pytoolbelt.core.error_handling.exceptions import PytoolbeltError
from pytoolbelt.core.project.tool_components import PtVenv, ToolConfig, ToolPaths
from pytoolbelt.core.project.toolbelt_components import ToolbeltPaths


def test_ptvenv_to_dict_returns_correct_dict():
    ptvenv = PtVenv(name="test_env", version="1.0")
    expected_dict = {"name": "test_env", "version": "1.0"}
    assert ptvenv.to_dict() == expected_dict


def test_ptvenv_to_dict_includes_all_keys():
    ptvenv = PtVenv(name="env", version="2.0")
    result_dict = ptvenv.to_dict()
    assert "name" in result_dict and "version" in result_dict


def test_ptvenv_to_dict_handles_empty_values():
    ptvenv = PtVenv(name="", version="")
    expected_dict = {"name": "", "version": ""}
    assert ptvenv.to_dict() == expected_dict


def test_toolconfig_from_file_with_valid_yaml(tmp_path):
    yaml_content = """
tool:
  name: "SampleTool"
  version: "1.0"
  ptvenv:
    name: "env"
    version: "3.8"
"""
    with (
        patch("builtins.open", mock_open(read_data=yaml_content)),
        patch(
            "yaml.safe_load",
            return_value={
                "tool": {"name": "SampleTool", "version": "1.0", "ptvenv": {"name": "env", "version": "3.8"}}
            },
        ),
    ):
        tool_config = ToolConfig.from_file(MagicMock())

        assert tool_config.name == "SampleTool"
        assert tool_config.version == "1.0"
        assert isinstance(tool_config.ptvenv, PtVenv)
        assert tool_config.ptvenv.name == "env"
        assert tool_config.ptvenv.version == "3.8"


def test_toolconfig_to_dict_returns_correct_structure():
    ptvenv = PtVenv(name="env", version="3.8")
    tool_config = ToolConfig(name="SampleTool", version="1.0", ptvenv=ptvenv)
    expected_dict = {"tool": {"name": "SampleTool", "version": "1.0", "ptvenv": {"name": "env", "version": "3.8"}}}
    assert tool_config.to_dict() == expected_dict


@pytest.fixture
def mock_component_metadata():
    return ComponentMetadata(name="TestTool", version="1.0.0", kind="tool")


@pytest.fixture
def mock_toolbelt_paths():
    return ToolbeltPaths(toolbelt_root=Path("/fake/toolbelt"))


@pytest.fixture
def tool_paths_instance(mock_component_metadata, mock_toolbelt_paths):
    return ToolPaths(meta=mock_component_metadata, toolbelt_paths=mock_toolbelt_paths)


def test_tool_paths_properties(tool_paths_instance, mock_component_metadata, mock_toolbelt_paths):
    # Testing all properties of ToolPaths
    assert tool_paths_instance.toolbelt_paths == mock_toolbelt_paths
    assert tool_paths_instance.meta == mock_component_metadata
    assert tool_paths_instance.tool_dir == mock_toolbelt_paths.tools_dir / mock_component_metadata.name
    assert tool_paths_instance.tool_code_dir == tool_paths_instance.tool_dir / mock_component_metadata.name
    assert tool_paths_instance.cli_dir == tool_paths_instance.tool_code_dir / "cli"
    assert tool_paths_instance.tests_dir == tool_paths_instance.tool_dir / "tests"
    assert tool_paths_instance.tool_config_file == tool_paths_instance.tool_dir / "config.yml"
    assert tool_paths_instance.readme_md_file == tool_paths_instance.tool_dir / "README.md"
    assert tool_paths_instance.dunder_main_file == tool_paths_instance.tool_code_dir / "__main__.py"
    assert tool_paths_instance.package_init_file == tool_paths_instance.tool_code_dir / "__init__.py"
    assert tool_paths_instance.dunder_cli_init_file == tool_paths_instance.cli_dir / "__init__.py"
    assert tool_paths_instance.cli_entrypoints_file == tool_paths_instance.cli_dir / "entrypoints.py"
    assert tool_paths_instance.install_path == Path.home() / ".pytoolbelt" / "tools" / mock_component_metadata.name
    assert tool_paths_instance.display_install_path == f"~/.pytoolbelt/tools/{mock_component_metadata.name}"
    assert tool_paths_instance.zipapp_path == Path(
        f"{tool_paths_instance.install_path.as_posix()}=={str(mock_component_metadata.version)}"
    )
    assert tool_paths_instance.dev_install_path == Path(f"{tool_paths_instance.install_path.as_posix()}-dev")
    assert tool_paths_instance.dev_symlink_path == tool_paths_instance.install_path
    assert tool_paths_instance.new_directories == [
        tool_paths_instance.tool_dir,
        tool_paths_instance.tool_code_dir,
        tool_paths_instance.cli_dir,
    ]
    assert tool_paths_instance.new_files == [
        tool_paths_instance.tool_config_file,
        tool_paths_instance.readme_md_file,
        tool_paths_instance.dunder_main_file,
        tool_paths_instance.package_init_file,
        tool_paths_instance.dunder_cli_init_file,
        tool_paths_instance.cli_entrypoints_file,
    ]


@patch("pathlib.Path.exists")
@patch("pathlib.Path.unlink")
@patch("pathlib.Path.symlink_to")
def test_create_install_symlink(mock_symlink_to, mock_unlink, mock_exists, tool_paths_instance):
    mock_exists.return_value = False
    tool_paths_instance.create_install_symlink()

    mock_symlink_to.assert_called_once()
    mock_unlink.assert_not_called()
    mock_exists.assert_called_once()


@patch("pathlib.Path.exists")
@patch("pathlib.Path.unlink")
@patch("pathlib.Path.symlink_to")
def test_create_install_symlink_symlink_exists(mock_symlink_to, mock_unlink, mock_exists, tool_paths_instance):
    mock_exists.return_value = True
    tool_paths_instance.create_install_symlink()

    mock_symlink_to.assert_called_once()
    mock_unlink.assert_called_once()
    mock_exists.assert_called_once()


def test_raise_if_exists(tool_paths_instance):
    with patch.object(Path, "exists", return_value=True):
        with pytest.raises(PytoolbeltError):
            tool_paths_instance.raise_if_exists()
