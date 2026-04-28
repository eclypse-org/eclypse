.DEFAULT_GOAL := check

check:
	pre-commit run -a

changelog:
	cz bump --changelog

patch:
	cz bump --changelog --increment patch

setup:
	python -m pip install --upgrade pip
	pip install poetry
	poetry config virtualenvs.create false
	echo "Poetry virtualenv creation disabled for CI. To re-enable, run `poetry config virtualenvs.create true`."

setup-build: setup
	poetry install --with=dev,deploy --no-root

setup-test: setup
	poetry install --with=test --no-root

format:
	isort eclypse
	ruff check
	ruff format

build: format
	poetry build -v --no-cache --format wheel

verify:
	twine check --strict dist/*

publish-test: build verify
	poetry publish -r test-pypi --skip-existing -v

publish: build verify
	poetry publish --skip-existing -v
