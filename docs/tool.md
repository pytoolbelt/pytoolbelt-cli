[![Blueprint fonts](https://see.fontimg.com/api/renderfont4/BWWo5/eyJyIjoiZnMiLCJoIjo4NywidyI6MTAwMCwiZnMiOjg3LCJmZ2MiOiIjMUNBN0ZGIiwiYmdjIjoiI0ZGRkZGRiIsInQiOjF9/UHl0b29sYmVsdA/typo-draft-demo.png)](https://www.fontspace.com/category/blueprint)

## What is a tool?
A `tool` is a stripped down python project that contains only your python code, as well as a single configuration file that tells `pytoolbelt` how to manage the tool.
`tools` have entrypoints, as well as a `ptvenv` that they require to run. This allows you to have multiple tools that share the same python environment, reducing the overhead of managing multiple virtual environments.

## Creating a tool
To create a `tool` from the toolbelt directory of your project, simply run the following command. Remember, the name of your tool
will be the name of the command itself, so choose wisely.

```bash
pytoolbelt tool new --name mytool
```

or globally, you can specify the toolbelt to use
```bash
pytoolbelt tool new --toolbelt my-toolbelt --name mytool
```

### Directory Structure
An example of what a `tool` directory structure looks like is as follows:
```
tools
├── mytool
│   ├── mytool
│   │   ├── __init__.py
│   │   ├── __main__.py
│   │   ├── cli
│   │   │  ├── __init__.py
│   │   │  ├── entrypoints.py
│   ├── config.yml
│   └── README.md
```

It is possible to change this structure as needed, however this is a good starting point for most tools that have a few entrypoints and arguments. 
If a simpler structure is needed, you can remove the `cli` directory and put all of your entrypoints in the `__main__.py` file and treat your tool as 
a single file python script. It is however required to have the `config.yml` file in the root of the tool directory as well as the `__init__.py` file in the `mytool` directory.

An example of what a simple tool layout looks like is as follows:
```
tools
├── mytool
│   ├── mytool
│   │   ├── __init__.py
│   │   ├── __main__.py
│   ├── config.yml
│   └── README.md
```

### Example Tool Config
```yaml
tool:
  name: mytool
  version: "0.0.1"
  ptvenv:
    name: "my_ptvenv"
    version: "0.0.1"
```
