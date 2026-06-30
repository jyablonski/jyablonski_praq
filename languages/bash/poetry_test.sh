#!/bin/bash

# Define the required poetry version
required_version="1.8.3"


# Get the installed poetry version
installed_version=$(poetry --version | grep -oP '\d+\.\d+\.\d+')

# Function to compare version numbers
version_lt() {
  [ "$1" != "$2" ] && [ "$(printf '%s\n' "$1" "$2" | sort -V | head -n1)" == "$1" ]
}

# Compare installed version with required version
if version_lt "$installed_version" "$required_version"; then
  echo "Your Poetry version is $installed_version. Version $required_version or higher is required."
  read -p "Do you want to update Poetry to the latest version? (y/n) " answer

  if [[ $answer == [Yy]* ]]; then
    echo "Updating Poetry..."
    curl -sSL https://install.python-poetry.org | python3 -
  else
    echo "Poetry update skipped."
  fi
else
  echo "Your Poetry version is $installed_version. No update is needed."
fi