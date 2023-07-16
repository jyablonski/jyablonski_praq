# New Docker Image w/ Poetry
[Link](https://github.com/orgs/python-poetry/discussions/1879)
1. Run `asdf local python 3.9.17` or whatever other Python version you want to use for the project
2. Run `poetry init` to build a new project.  name is whatever and leave all the other defaults on.
3. If your Poetry project is just used for environment management and isn't an actual package:
   1. Delete the `packages = [{ include = "my_package" }]` line
   2. This tells Poetry to expect that package to be included after it installs, but it'll start failing if you don't have one
4. Install new packages to your Poetry project with `Poetry add pandas` etc.
5. Copy the `Dockerfile` in this folder & voila.

