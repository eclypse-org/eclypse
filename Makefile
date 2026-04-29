.DEFAULT_GOAL := check

PYTHON ?= python3

check:
	pre-commit run -a

changelog:
	cz bump --changelog

patch:
	cz bump --changelog --increment patch

setup:
	$(PYTHON) -m pip install --upgrade pip uv poetry

setup-build: setup
	uv sync --group dev --group deploy --no-install-project

setup-test: setup
	uv sync --group test --no-install-project

format:
	uv run --no-sync isort eclypse
	uv run --no-sync ruff check
	uv run --no-sync ruff format

verify:
	uv run --no-sync twine check --strict dist/*

build: format
	uv build --wheel --clear

publish-test: build verify
	uv publish --index testpypi -v

publish: build verify
	uv publish -v


# build: format
# 	poetry build -v --no-cache --format wheel

# publish-test: build verify
# 	poetry publish -r test-pypi --skip-existing -v

# publish: build verify
# 	poetry publish --skip-existing -v
