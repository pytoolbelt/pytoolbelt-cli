from pytoolbelt.core.bases.base_templater import BaseTemplater


class NoxfileTemplater(BaseTemplater):
    def render_noxfile(self, ptvenvs) -> str:
        return self.render("noxfile.py.jinja2", ptvenvs=ptvenvs)


class PytestIniTemplater(BaseTemplater):
    def render_pytest_ini(self, tools) -> str:
        return self.render("pytest.ini.jinja2", tools=tools)
