.DEFAULT_GOAL := check

setup:
	uv sync --locked --all-groups

check:
	uv run pre-commit run -a

bump:
	uv run cz bump

patch:
	uv run cz bump --increment patch

format:
	uv run isort eclypse tests
	uv run ruff check
	uv run ruff format

docs:
	uv run --group docs $(MAKE) -C docs html

verify:
	uvx twine check --strict dist/*

build:
	uv build --wheel --clear --no-create-gitignore

publish: build verify
	uv publish -v

.PHONY: setup check bump patch format docs verify build publish
