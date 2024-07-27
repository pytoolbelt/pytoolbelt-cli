[![Blueprint fonts](https://see.fontimg.com/api/renderfont4/BWWo5/eyJyIjoiZnMiLCJoIjo4NywidyI6MTAwMCwiZnMiOjg3LCJmZ2MiOiIjMUNBN0ZGIiwiYmdjIjoiI0ZGRkZGRiIsInQiOjF9/UHl0b29sYmVsdA/typo-draft-demo.png)](https://www.fontspace.com/category/blueprint)

## What is a ptvenv?
A `ptvenv` is simply a `yaml` file that has a minimal python environment definition. This environment will be built using `pytoolbelt`, which will
put the resulting python environment in a consistent location which can be referenced when developing and installing your tools. 
This allows multiple tools to share the same python environment, reducing the development overhead of having to manage an environment
for each tool, as with more traditional python virtual environments.

## Creating a ptvenv
To create a `ptvenv` from the toolbelt directory of your project, simply run the following command
```bash
pytoolbelt ptvenv new --name my_ptvenv
```
or globally, you can specify the toolbelt to use
```bash
pytoolbelt ptvenv new --toolbelt my-toolbelt --name my_ptvenv
```

### Directory Structure
An example of what a `ptvenv` directory structure looks like is as follows:

```
ptvenv
├── myptvenv
│   ├── myptvenv.yml   -- The ptvenv configuration file
│   └── README.md      -- A README file for the ptvenv
```

### Example Definition
```yaml
name: my_ptvenv
version: "0.1.0"
python_version: "3.10"
requirements:
    - pytoolbelt-toolkit==0.4.0
    - pyyaml==6.0.1
    - python-dotenv==1.0.0
    - requests==2.32.3
```

Each key in the `yml` file has the following meaning

- `name (string)` An arbitrary, but meaningful name for the `ptvenv`
- `version (string)` The semantic version for the `ptvenv` (must be quoted)
- `python_version (string)` The version of python required to create the `ptvenv`. (must be quoted)
- `requrements (list[string])` A list of requirements following the same syntax as accepted in a `requirements.txt` file.

The requirements section is optional. If your tools do not require any additional dependencies to operate, then leave this list empty.

## Installing the ptvenv
To build and install a `ptvenv`, simply cd to the directory containing the `ptvenv` definition and run
```bash
pytoolbelt ptvenv install --name my_ptvenv
```
Or from any directory by specifying the toolbelt to find the definition in
```bash
pytoolbelt ptvenv install --toolbelt my-toolbelt --name my_ptvenv
```

If a specific version of a `ptvenv` has been released in the repo, you can specify the version to install using the == syntax
```bash
pytoolbelt ptvenv install --toolbelt my-toolbelt --name my_ptvenv==1.22.3
```
