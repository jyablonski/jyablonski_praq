import warnings
from packaging import version
# import pkg_resources

import polars as pl

# Define the package and required version
package_name = "example_package"
required_version = version.parse("2.0.0")
current_version = version.parse(pl.__version__)

# Compare versions
if current_version < required_version:
    warnings.warn(
        f"You are using {package_name} version {pl.__version__}, which is outdated. "
        f"Please upgrade to version {required_version} or newer.",
        UserWarning
    )

# Your code continues here
