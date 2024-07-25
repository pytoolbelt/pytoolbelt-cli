import nox


@nox.session
def check_formating(session):
    requirements = nox.project.load_toml("pyproject.toml")["project"]["optional-dependencies"]["fmt"]
    session.install(*requirements)
    session.run("black", "--check", "pytoolbelt", "tests")
    session.run("isort", "--check-only", "pytoolbelt", "tests")


@nox.session(python=['3.9', '3.10', '3.11', '3.12'])
def tests(session):
    requirements = nox.project.load_toml("pyproject.toml")["project"]["dependencies"]
    session.install(*requirements)
    session.install('pytest')
    session.run('pytest')
