#!/usr/bin/env bash

set -euo pipefail

uv sync --locked --group dev --group test --group docs
uv run --no-sync pre-commit install

mkdir -p "$HOME/.local/share/zsh/site-functions"

uv generate-shell-completion zsh > "$HOME/.local/share/zsh/site-functions/_uv"
uvx --generate-shell-completion zsh > "$HOME/.local/share/zsh/site-functions/_uvx"
