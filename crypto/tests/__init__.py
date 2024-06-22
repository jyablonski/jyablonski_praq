# Marks the tests directory as a package
# without this, the `from crypto.api_scrape import get_bitcoin_information`
# wont work

# In Python, __init__.py files are used to mark directories on disk as Python package directories.
# This allows you to use the package structure for imports. However, since Python 3.3,
# implicit namespace packages were introduced, which allow you to create packages without an __init__.py file.

# In the context of your crypto/tests/unit/ directory, whether you need an __init__.py file depends on a few factors:
