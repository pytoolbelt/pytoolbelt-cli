import requests
from pathlib import Path
from pytoolbelt.core.error_handlers import handle_http_errors
from pytoolbelt.core.exceptions import PyEnvDownloadError, PyEnvUploadError


@handle_http_errors(exception=PyEnvDownloadError, msg="PyToolBelt :: Unable to download pyenv :: ")
def download_pyenv_metadata_file(path: Path, url: str) -> requests.Response:
    response = requests.get(url)
    response.raise_for_status()

    with path.open("wb") as file:
        file.write(response.content)

    return response


@handle_http_errors(exception=PyEnvUploadError, msg="PyToolBelt :: Unable to upload pyenv :: ")
def upload_pyenv_metadata_file(path: Path, url: str) -> requests.Response:
    with path.open("rb") as file:
        files = {"file": file}
        return requests.post(url, files=files)


@handle_http_errors(exception=PyEnvUploadError, msg="PyToolBelt :: Unable to upload pyenv :: ")
def post_pyenv_metadata(data: dict, url: str) -> requests.Response:
    return requests.post(url, json=data)


@handle_http_errors(exception=PyEnvDownloadError, msg="PyToolBelt :: Unable to download pyenv :: ")
def get_pyenv_metadata(url: str) -> requests.Response:
    response = requests.get(url)
    response.raise_for_status()
    return response
