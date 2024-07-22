class PythonEnvBuildError(Exception):
    pass


class RepoConfigNotFoundError(Exception):
    pass


class NotOnReleaseBranchError(Exception):
    pass


class UncommittedChangesError(Exception):
    pass


class UnableToReleaseError(Exception):
    pass


class LocalAndRemoteHeadAreDifferentError(Exception):
    pass


class CliArgumentError(Exception):
    pass


class PtVenvCreationError(Exception):
    pass


class PtVenvNotFoundError(Exception):
    pass


class ToolCreationError(Exception):
    pass


class ToolbeltConfigNotFound(Exception):
    pass


class NotPytoolbeltProjectError(Exception):
    pass


class PytoolbeltConfigNotFoundError(Exception):
    pass


class CreateReleaseError(Exception):
    pass


class ToolbeltExistsError(Exception):
    pass


class ToolbeltFetchError(Exception):
    pass


class PytoolbeltError(Exception):
    pass
