[![Blueprint fonts](https://see.fontimg.com/api/renderfont4/BWWo5/eyJyIjoiZnMiLCJoIjo4NywidyI6MTAwMCwiZnMiOjg3LCJmZ2MiOiIjMUNBN0ZGIiwiYmdjIjoiI0ZGRkZGRiIsInQiOjF9/UHl0b29sYmVsdA/typo-draft-demo.png)](https://www.fontspace.com/category/blueprint)

## What is a tool?
A `tool` is a stripped down python project that contains only your python code, as well as a single configuration file that tells `pytoolbelt` how to manage the tool.
`tools` have entrypoints, as well as a `ptvenv` that they require to run. This allows you to have multiple tools that share the same python environment, reducing the overhead of managing multiple virtual environments.

## Creating a tool
To create a `tool` from the toolbelt directory of your project, simply run the following command
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

### Example Tool Config
```yaml
tool:
  name: mytool
  version: "0.0.1"
  ptvenv:
    name: "my_ptvenv"
    version: "0.0.1"
```
