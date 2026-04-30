.DEFAULT_GOAL := check

check:
	pre-commit run -a

changelog:
	cz bump --changelog

patch:
	cz bump --changelog --increment patch

setup-build:
	uv sync --group dev --group deploy --no-install-project

setup-test:
	uv sync --group test --no-install-project

format:
	isort eclypse
	ruff check
	ruff format

verify:
	twine check --strict dist/*

build: format
	uv build --wheel --clear --no-create-gitignore

publish-test: build verify
	UV_PUBLISH_TOKEN="$$UV_TEST_PYPI_ECLYPSE" uv publish --index testpypi -v

publish: build verify
	uv publish -v
