import nox
import tomllib
from pathlib import Path


def get_requirements():
    tomlpath = Path(__file__).parent / 'pyproject.toml'

    with tomlpath.open("rb") as fp:
        data = tomllib.load(fp)
        return data['project']['dependencies']


@nox.session(python=['3.8', '3.9', '3.10', '3.11', '3.12'])
def tests(session):
    session.install(*get_requirements())
    session.install('pytest')
    session.run('pytest')
