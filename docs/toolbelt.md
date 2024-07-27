[![Blueprint fonts](https://see.fontimg.com/api/renderfont4/BWWo5/eyJyIjoiZnMiLCJoIjo4NywidyI6MTAwMCwiZnMiOjg3LCJmZ2MiOiIjMUNBN0ZGIiwiYmdjIjoiI0ZGRkZGRiIsInQiOjF9/UHl0b29sYmVsdA/typo-draft-demo.png)](https://www.fontspace.com/category/blueprint)

# Toolbelt

## What is a Toolbelt?
`pytoolbelt` is opinionated, and manages a specific directory structure within a `toolbelt` repository. A minimum toolbelt directory structure looks like this:

```
ptvenv           -- This is where your venv definitions live
tools            -- This is where your tools live
.gitignore       -- standard gitignore file
pytoolbelt.yml   -- The pytoolbelt configuration file for this toolbelt
```

### The ptvenv Directory
This directory contains all the venv definitions for your tools, referred to as a `ptvenv`. Each `ptvenv` is given a name, and a version as well as the python version required for it to work, 
and the requirements that are needed for the venv. An example looks like this:

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
```

Each key in the `yml` file has the following meaning
`python (string)` The version of python used to create new `ptvenv`s. (must be quoted)
`bump (string)` The default bump level for the `bump` command. (must be quoted)
`envfile (string)` The path of the `.env` file that will be used to store environment variables. (must be quoted)
'release_branch (string)` The branch that will be used to create new releases. (must be quoted)'
