[![Blueprint fonts](https://see.fontimg.com/api/renderfont4/BWWo5/eyJyIjoiZnMiLCJoIjo4NywidyI6MTAwMCwiZnMiOjg3LCJmZ2MiOiIjMUNBN0ZGIiwiYmdjIjoiI0ZGRkZGRiIsInQiOjF9/UHl0b29sYmVsdA/typo-draft-demo.png)](https://www.fontspace.com/category/blueprint)

# Pytoolbelt Directories

`pytoolbelt` allows you to manage your python tools and scripts in a single repository, and share them with your team. 
This repository is called a `toolbelt`. Pytoolbelt can manage many `toolbelts` on your system, and allows you to install and run tools from them.
After running `pytoolbelt init`, you can add the `~/.pytoolbelt/tools` directory to your `$PATH` either by running `pytoolbelt init --path`
or by manually adding it to your `.bashrc` or `.zshrc` file.

## Pytoolbelt Directories
`pytoolbelt` requires the following directories to be present on your system:

- `~/.pytoolbelt` - The root directory where all venvs and toolbelts are installed.
- `~/.pytoolbelt/environments` - The directory where all venvs are installed.
- `~/.pytoolbelt/tools` - The directory where all tools are installed.
- `~/pytoolbelt/toolbelts` - The directory where all toolbelts are installed.

### The toolbelts.yml file
The `toolbelts.yml` file is a configuration file that contains the list of all toolbelts that are installed on your system.
It is located at `~/.pytoolbelt/toolbelts.yml`.
