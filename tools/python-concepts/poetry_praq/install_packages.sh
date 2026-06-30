#!/bin/bash

set -euo pipefail

export DEBIAN_FRONTEND=noninteractive

apt-get update
apt-get -y upgrade
apt-get -y install --no-install-recommends gcc

pip install --upgrade pip
apt-get install -y --no-install-recommends curl \
    && curl -sSL https://install.python-poetry.org | python3 -

apt-get clean
rm -rf /var/lib/apt/lists/*