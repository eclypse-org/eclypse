.DEFAULT_GOAL := check

setup:
	uv sync --locked --all-groups

check:
	uv run pre-commit run -a

bump:
	uv run cz bump

patch:
	uv run cz bump --increment patch

docs:
	uv run --group docs zensical build --strict

docs-serve:
	uv run --group docs zensical serve

verify:
	uvx twine check --strict dist/*

build:
	uv build --wheel --clear --no-create-gitignore

publish: build verify
	uv publish -v

.PHONY: setup check bump patch docs docs-serve verify build publish
