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
