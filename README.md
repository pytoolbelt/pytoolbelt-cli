[![Blueprint fonts](https://see.fontimg.com/api/renderfont4/BWWo5/eyJyIjoiZnMiLCJoIjo4NywidyI6MTAwMCwiZnMiOjg3LCJmZ2MiOiIjMUNBN0ZGIiwiYmdjIjoiI0ZGRkZGRiIsInQiOjF9/UHl0b29sYmVsdA/typo-draft-demo.png)](https://www.fontspace.com/category/blueprint)

### Sharing python tooling within your organization, the easy way.

## What is Pytoolbelt?
Pytoolbelt is a CLI, written in python, intended to remove the barrier to developing, sharing, testing and documenting internal tooling
within your organization. 

It treats a standard git repo as a `toolbelt`, which is basically a mono repo with all of your python tools and scripts that you want to share and document for use within your organization.

It also allows your team to define one or more python environments (venv) that can be re-used for multiple tools. 

## Why Pytoolbelt?
Python is a wonderful language for writing scripts and small tools, but sharing them within your organization can be a pain.
`virtual environments`, `requirements.txt`, `setup.py`, `makefile`,  `pyproject.toml` packaging, versioning, documentation, testing, public / private artifact repositories (pypi) etc.... 

Pytoolbelt takes care of all of that for you. It leverages
best practices and existing tools in the python ecosystem to make it easy to share your tools with your colleagues.


## Getting Started
pytoolbelt can be installed via pip:
```bash
pip install pytoolbelt-cli
```
