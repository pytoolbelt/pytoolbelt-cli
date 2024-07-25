import pytest
from semver import Version

from pytoolbelt.core.data_classes.component_metadata import ComponentMetadata
from pytoolbelt.core.error_handling.exceptions import CliArgumentError


def test_component_metadata_initialization_with_valid_data():
    metadata = ComponentMetadata("test_component", "1.0.0", "tool")
    assert metadata.name == "test_component"
    assert metadata.version == Version.parse("1.0.0")
    assert metadata.kind == "tool"


def test_component_metadata_initialization_with_latest_version():
    metadata = ComponentMetadata("test_component", "latest", "tool")
    assert metadata.version == "latest"


def test_component_metadata_from_string_with_valid_data():
    metadata = ComponentMetadata.from_string("test_component==1.0.0", "tool")
    assert metadata.name == "test_component"
    assert metadata.version == Version.parse("1.0.0")


def test_component_metadata_from_string_with_latest_version():
    metadata = ComponentMetadata.from_string("test_component", "tool")
    assert metadata.version == "latest"


def test_component_metadata_from_string_raises_exception_with_invalid_version():
    with pytest.raises(CliArgumentError):
        ComponentMetadata.from_string("test_component==invalid", "tool")


def test_component_metadata_raise_if_forbidden_char_in_name_raises_exception():
    with pytest.raises(CliArgumentError):
        ComponentMetadata("test@component", "1.0.0", "tool").raise_if_forbidden_char_in_name()


def test_component_metadata_is_not_prerelease_returns_correct_value():
    prerelease_metadata = ComponentMetadata("test_component", "1.0.0-alpha.1", "tool")
    stable_metadata = ComponentMetadata("test_component", "1.0.0", "tool")
    assert not prerelease_metadata.is_not_prerelease()
    assert stable_metadata.is_not_prerelease()


def test_component_metadata_release_tag_formats_correctly():
    metadata = ComponentMetadata("test_component", "1.0.0", "tool")
    assert metadata.release_tag == "tool-test_component-1.0.0"


def test_component_metadata_is_latest_version_identifies_latest_correctly():
    latest_metadata = ComponentMetadata("test_component", "latest", "tool")
    versioned_metadata = ComponentMetadata("test_component", "1.0.0", "tool")
    assert latest_metadata.is_latest_version
    assert not versioned_metadata.is_latest_version
