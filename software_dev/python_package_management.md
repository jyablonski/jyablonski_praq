# Python Package Management Files

### setup.py
Old de facto standard for packaging.  It's a raw python script that installs the associated package. It did its job but new tools are around that do the job better.  Sometimes accompanied by a `setup.cfg` file.

### pyproject.toml
The new standardized format to describe project metadata.  Easier to work wtih and allows for a number of configurations for different Python tools such as linters, tests, and versions from 1 file.


## Poetry
Poetry sits on top of `pyproject.toml` to manage metadata for your project, Package management and versioning, other plugins config options such as Tox, Pytest, Linters like Black + Flake8 etc all from 1 file.

## Wheels
[Article](https://realpython.com/python-wheels/)

Python Wheels are pre-built bundles of packages that you install via Pip.  The alternative is for you to download the source installation for a package and then compile it yourself, which takes time.  Pip automatically tries finding & using wheels for packages if they're available.  
- Different wheels depending on OS such as Windows, Mac, or Linux.
- Some packages don't offer wheels because of how complex they are.
- Wheels are typically smaller in size to download, and faster to install from than a source distribution.
- Installing from source distributions often requires special compilation libraries like gcc or OpenSSL.  With wheels, you dont have to worry about this.
- Wheels target specific OS platform's and Python versions.


Python Egg or .egg-info is metadata related to the package to help specify package dependencies and other things.  Users aren't affected by it.