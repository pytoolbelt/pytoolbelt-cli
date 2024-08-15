from unittest.mock import patch

import pytest

from pytoolbelt.core.tools.noxtemplating import NoxfileTemplater, PytestIniTemplater


@pytest.fixture
def noxfile_templater():
    return NoxfileTemplater()


@pytest.fixture
def pytest_ini_templater():
    return PytestIniTemplater()


@patch.object(NoxfileTemplater, "render", return_value="rendered_noxfile")
def test_render_noxfile(mock_render, noxfile_templater):
    ptvenvs = ["ptvenv1", "ptvenv2"]
    result = noxfile_templater.render_noxfile(ptvenvs)
    mock_render.assert_called_once_with("noxfile.py.jinja2", ptvenvs=ptvenvs)
    assert result == "rendered_noxfile"


@patch.object(PytestIniTemplater, "render", return_value="rendered_pytest_ini")
def test_render_pytest_ini(mock_render, pytest_ini_templater):
    tools = ["tool1", "tool2"]
    result = pytest_ini_templater.render_pytest_ini(tools)
    mock_render.assert_called_once_with("pytest.ini.jinja2", tools=tools)
    assert result == "rendered_pytest_ini"
