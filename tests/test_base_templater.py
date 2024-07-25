import pytest
from jinja2 import PackageLoader

from pytoolbelt.core.bases.base_templater import BaseTemplater


@pytest.fixture
def templater():
    return BaseTemplater()


def test_environment_initialization_sets_correct_loader(templater):
    assert isinstance(templater.jinja_env.loader, PackageLoader)


def test_format_template_name_appends_jinja2_extension(templater):
    formatted_name = templater.format_template_name("test_template")
    assert formatted_name == "test_template.jinja2"


def test_render_renders_template_with_provided_context(templater):
    rendered_content = templater.render("sample_template.jinja2", name="World")
    assert "Hello, World!" in rendered_content


def test_render_raises_exception_for_nonexistent_template(templater):
    with pytest.raises(Exception):
        templater.render("nonexistent_template")
