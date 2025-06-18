#!/usr/bin/env bash
set -eu

# Enable debug mode if DEBUG=true is set in the environment
DEBUG=${DEBUG:-false}
if [ "$DEBUG" = "true" ]; then
  set -x
fi

# Resolve project root directory
my_path=$(git rev-parse --show-toplevel)

uv run mypy src
