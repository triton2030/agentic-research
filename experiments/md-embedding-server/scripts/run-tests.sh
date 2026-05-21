#!/usr/bin/env bash
# Run the md-navigator test suite in an isolated uv environment.
# Mirrors the inline-deps of md_navigator.py plus pytest itself.
set -euo pipefail
cd "$(dirname "$0")/.."
exec uv run \
  --with pytest \
  --with numpy \
  --with sqlite-vec \
  --with pyyaml \
  --with pymorphy3 \
  pytest tests/ "$@"
