[![Blueprint fonts](https://see.fontimg.com/api/renderfont4/BWWo5/eyJyIjoiZnMiLCJoIjo4NywidyI6MTAwMCwiZnMiOjg3LCJmZ2MiOiIjMUNBN0ZGIiwiYmdjIjoiI0ZGRkZGRiIsInQiOjF9/UHl0b29sYmVsdA/typo-draft-demo.png)](https://www.fontspace.com/category/blueprint)

# CLI Reference

## Organization
The `pytoolbelt` CLI organizes its commands in the following way:
```bash
pytoolbelt <command> <subcommand> <options>
```
Where `<command>` is a noun `<subcommand>` is a verb and `<options>` are the flags and arguments that the command accepts.

example -> Creating a new tool:
```bash
pytoolbelt tool new --name mytool
```

## Help
At any level of the command hierarchy, you can get help by running the command with the `--help` or `-h` flag. This will print out the help for the command and all of its subcommands.

## Commands
The following is a list of commands that `pytoolbelt` supports:

### Toolbelt
The `toolbelt` command is used to manage the `toolbelt` repository. This includes creating a new `toolbelt`, or cloning an existing `toolbelt`.

### Tool
The `tool` command is used to manage the `tools` within a `toolbelt`. This includes creating a new `tool`, and installing a `tool`.

### Ptvenv
The `ptvenv` command is used to manage the `ptvenv` within a `toolbelt`. This includes creating a new `ptvenv`, and installing a `ptvenv`.

### Release
The `release` command is used to manage the `releases` within a `toolbelt`. This includes creating a new `release`.
