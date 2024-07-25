[![Blueprint fonts](https://see.fontimg.com/api/renderfont4/BWWo5/eyJyIjoiZnMiLCJoIjo4NywidyI6MTAwMCwiZnMiOjg3LCJmZ2MiOiIjMUNBN0ZGIiwiYmdjIjoiI0ZGRkZGRiIsInQiOjF9/UHl0b29sYmVsdA/typo-draft-demo.png)](https://www.fontspace.com/category/blueprint)

# Currently in BETA Development - Not production ready!

### Sharing python tooling within your organization, the easy way.

## What is Pytoolbelt?
Pytoolbelt is a CLI, written in python, intended to remove the barrier to developing, sharing, testing and documenting internal tooling written in python
within your organization. 

It treats a standard git repo as a `toolbelt`, which is basically a mono repo with all of your python tools and scripts that you want to share and document for use within your organization.

It also allows your team to define one or more python environments (venv) that can be re-used for multiple tools, and facilitates installing your tools as a zipapp, which can be run globally from your terminal. 

## Why Pytoolbelt?
Python is a wonderful language for writing scripts and small tools, but sharing them within your organization can be a pain.
`virtual environments`, `requirements.txt`, `setup.py`, `makefile`,  `pyproject.toml` packaging, versioning, documentation, testing, public / private artifact repositories (pypi) etc.... 

Pytoolbelt takes care of all of that for you. It leverages
best practices and existing tools in the python ecosystem to make it easy to share your tools with your colleagues.

## Getting Started
pytoolbelt can be installed via pip (venv creation recommended):
```bash
pip install pytoolbelt-cli
```

`pytoolbelt` is also intended to be installed globally if desired. If that is the case, It is recommended to be installed via `pipx`
```bash
pipx install pytoolbelt-cli
```
Pipx is a tool that can be considered a "homebrew" for tools written in python. More information on `pipx` can be found [here](https://pipx.pypa.io/stable/installation/)

### Initialize pytoolbelt
To initialize a new pytoolbelt project and add the required directories to your `$PATH`, run the following command:
```bash
pytoolbelt init --path
```

### Video Tutorials
Head over to the pytoolbelt YouTube channel for video tutorials on how to use pytoolbelt:
[Pytoolbelt YouTube Channel](https://www.youtube.com/channel/UCRz_AcS2QLVIUvh2nfBWgRQ)

As pytoolbelt allows the installation of python tools from a `toolbelt`, it must also be added to your `$PATH` by running
```bash
pytoolbelt init --path
```
this will add the `~/.pytoolbelt/tools` directory to your `$PATH` in your `.bashrc` or `.zshrc` file.

## License
This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
