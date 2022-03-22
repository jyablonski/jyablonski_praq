#!/bin/bash

# run chmod 777 release_step.sh initially
# Check the CHANGELOG
# Use awk to check the number of non-header lines with stuff in them
awk '/^## \[U/,/^## \[[0-9]/' CHANGELOG.md
if [ $? -ne 0 ]; then
    echo 'bump changelog failure: nothing added to [Unreleased Section]'
    exit 1
fi

# check bumpversion and parse the new version using awk
set -eo pipefail
new_version="$(python3 -m bumpversion $1 --dry-run --list | awk -F'=' '/new_version/ {print $2}')"

# do the bump, update changelog using sed
sed -i 's/## \[Unreleased\]/## \[Unreleased\]\n\n\n## \['$new_version'\] - '$(date +%Y-%m-%d)'/g' CHANGELOG.md
git commit -am "bump CHANGELOG to $new_version"
python3 -m bumpversion $1 --verbose