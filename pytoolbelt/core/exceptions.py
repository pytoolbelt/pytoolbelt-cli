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
