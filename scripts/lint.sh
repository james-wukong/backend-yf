#!/usr/bin/env bash

set -e
set -x

# memory exceeded issue, comment ```mypy app```, check this locally
# mypy app
ruff check app --select I --fix
ruff format app --check
