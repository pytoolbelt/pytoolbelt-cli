import nox


@nox.session(python=['3.8', '3.9', '3.10', '3.11', '3.12'])
def tests(session):
    requirements = nox.project.load_toml("pyproject.toml")["project"]["dependencies"]
    session.install(*requirements)
    session.install('pytest')
    session.run('pytest')
