[![Blueprint fonts](https://see.fontimg.com/api/renderfont4/BWWo5/eyJyIjoiZnMiLCJoIjo4NywidyI6MTAwMCwiZnMiOjg3LCJmZ2MiOiIjMUNBN0ZGIiwiYmdjIjoiI0ZGRkZGRiIsInQiOjF9/UHl0b29sYmVsdA/typo-draft-demo.png)](https://www.fontspace.com/category/blueprint)

### Sharing python tooling within your organization, the easy way.

## What is Pytoolbelt?
Pytoolbelt is a CLI, intended to simplify creating and sharing python tools within your organization.
It treats a standard git repo as a `toolbelt`, which is a mono repo with all of your python tools you want to share within your organization.
It also allows your team to define one or more python environments (venv) that can be re-used for multiple tools, 
Tools are installed as a zipapp from source, which can be run globally from your terminal. 

## Why Pytoolbelt?
Python is a wonderful language for writing scripts and small tools, but sharing them within your organization can be a pain.
Navigating the python packaging ecosystem can be daunting, and creating a package for a simple script can be overkill. Not to mention that if you want to be able to `pip install` your tool, you need either to publish it to PyPi 
or to have a private package server (aka artifact repo), which is not always desirable or simply too much work.

Pytoolbelt aims to simplify this process by treating a git repo as a `toolbelt`. Installation is a simple as cloning the repo and running 
`pytoolbelt tool install --name <toolname>`, and the tool is installed as a zipapp, which can be run globally from your terminal.

## Documentation
Check out the full documentation at github pages [here](https://pytoolbelt.github.io/pytoolbelt-cli/)


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
this will add the `~/.pytoolbelt/tools` directory to your `$PATH` in your `.bashrc` or `.zshrc` file.

### Video Tutorials
Head over to the pytoolbelt YouTube channel for video tutorials on how to use pytoolbelt:
[Pytoolbelt YouTube Channel](https://www.youtube.com/channel/UCRz_AcS2QLVIUvh2nfBWgRQ)


## License
This project is licensed under the Apache License 2.0 - see the [LICENSE](LICENSE) file for details.
