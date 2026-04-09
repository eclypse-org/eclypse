#!/usr/bin/env bash

set -euo pipefail

poetry install --with dev,test,docs --extras=remote --extras=tboard
POETRY_ENV_PATH="$(poetry env info --path)"

for rc_file in "$HOME/.zshrc" "$HOME/.bashrc"; do
    marker_start="# >>> eclypse poetry env >>>"
    marker_end="# <<< eclypse poetry env <<<"

    touch "$rc_file"

    if grep -Fq "$marker_start" "$rc_file"; then
        tmp_file="$(mktemp)"
        awk -v start="$marker_start" -v end="$marker_end" '
            $0 == start { skip = 1; next }
            $0 == end { skip = 0; next }
            skip != 1 { print }
        ' "$rc_file" > "$tmp_file"
        mv "$tmp_file" "$rc_file"
    fi

    cat <<EOF >> "$rc_file"
$marker_start
if [ -f "$POETRY_ENV_PATH/bin/activate" ]; then
    source "$POETRY_ENV_PATH/bin/activate"
fi
$marker_end
EOF
done

source "$POETRY_ENV_PATH/bin/activate"
poetry run pre-commit install
