[![Blueprint fonts](https://see.fontimg.com/api/renderfont4/BWWo5/eyJyIjoiZnMiLCJoIjo4NywidyI6MTAwMCwiZnMiOjg3LCJmZ2MiOiIjMUNBN0ZGIiwiYmdjIjoiI0ZGRkZGRiIsInQiOjF9/UHl0b29sYmVsdA/typo-draft-demo.png)](https://www.fontspace.com/category/blueprint)

# Making Releases

## What is a release?
All releases are managed through the `pytoolbelt` tool. A `release` is a snapshot of your project at a specific point in time. This snapshot includes the code. A release can be made for either a `tool` or a `ptvenv`. It is best to envision
your toolbelt repo as a mono repo for all tools and environments that you manage, therefore a release can be made for any of the tools or environments that you have in your toolbelt.

## Creating a Release
Let's say you have a tool called "webcheck" that simply pings a website and returns the status code. You have made some changes to the tool and you want to release it. To do this, you would follow the steps below:

1. First, develop your tool until you are ready to release it.
2. Commit your changes to the toolbelt repository, pushing all changes to the remote release branch configured in `pytoolbelt.yml`.
3. Once you are ready to release your tool, bump the version number with the following command:

```bash
pytoolbelt tool bump --name webcheck  
```
This will bump the version number in the `config.yml` file of the tool. Obviously, you can also manually bump the version number in the `config.yml` file if you prefer.

4. Commit all of your changes including your version bump and push them to the remote repository release branch.
5. Alternatively you could make and merge a Pull Request to the configured release branch of the toolbelt repository.
6. If you merged via PR, once your changes are in the release branch, pull the latest changes from the remote repository.
7. Run the following command to create a release for the tool:

```bash
pytoolbelt release
```
