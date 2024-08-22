[![Blueprint fonts](https://see.fontimg.com/api/renderfont4/BWWo5/eyJyIjoiZnMiLCJoIjo4NywidyI6MTAwMCwiZnMiOjg3LCJmZ2MiOiIjMUNBN0ZGIiwiYmdjIjoiI0ZGRkZGRiIsInQiOjF9/UHl0b29sYmVsdA/typo-draft-demo.png)](https://www.fontspace.com/category/blueprint)

# Toolbelt

## What is a Toolbelt?
A toolbelt is simply a git repo with an opinionated directory structure that `pytoolbelt` uses to manage 
the development and installation of tools from a central location. A `toolbelt` can be considered a mono-repo and has the following structure.

```
ptvenv           -- This is where your venv definitions live
tools            -- This is where your tools live
.gitignore       -- standard gitignore file
pytoolbelt.yml   -- The pytoolbelt configuration file for this toolbelt
noxfile.py       -- The nox configuration file for this toolbelt. Nox is testing is optional
pytest.ini       -- The pytest configuration file for this toolbelt. Pytest is optional. 
```

### The ptvenv Directory
This directory contains all the venv definitions for your tools, referred to as a `ptvenv`. Each `ptvenv` is given a name, and a version as well as the python version required for it to work, 
and the requirements that are needed for the venv.

### The tools Directory
This directory contains all the tools that are part of your toolbelt. Each tool is given a name, and a version as well as the ptvenv required for it to work.

### The pytoolbelt.yml File
This file contains the configuration for the toolbelt and has the following structure.


```yaml
project-config:
    python: "3.10"
    bump: "minor"
    envfile: ".env"
    release_branch: "main"
    test_image: "pytoolbelt/nox-test-runner:0.0.1"
```

Each key in the `yml` file has the following meaning
- `python (string)` The version of python used to create new `ptvenv`s. (must be quoted)
- `bump (string)` The default bump level for the `bump` command. (must be quoted)
- `envfile (string)` The path of the `.env` file that will be used to store environment variables. (must be quoted)
- `release_branch (string)` The branch that will be used to create new releases. (must be quoted)'
- `test_image (string)` The docker image that will be used to run tests. (must be quoted)

## Create a new Toolbelt
To create a new toolbelt, simply run the following command 
```bash
pytoolbelt toolbelt new --url <git-repo-url>
```
Pytoolbelt needs to be linked to a remote git repo to manage the repo as a "toolbelt". The `--url` flag is required to link the toolbelt to the remote repo.
It is advised to first create the remote repo in your github (or other git provider) account before running this command. It is however not required.

This created a new toolbelt repo at the location `~/pytoolbelt/toolbelts/<toolbelt-name>`. A git repo was initiallized automatically at this location.


## Fetch a Toolbelt
To fetch a toolbelt first add the URL to the pytoolbelt config with the following command
```bash
pytoolbelt toolbelt add --url <git-repo-url>
```

Once the toolbelt has been added to the config, it can be fetch with the following command
```bash
pytoolbelt toolbelt fetch --name <toolbelt-name>
```

## Display Configured Toolbelts
To display the configured toolbelts, run the following command
```bash
pytoolbelt toolbelt show
```

## Remove a Toolbelt
To remove a toolbelt from the configuration, run the following command
```bash
pytoolbelt toolbelt remove --name <toolbelt-name>
```
The delete the repo from your machine
```bash
rm -rf ~/pytoolbelt/toolbelts/<toolbelt-name>
```
