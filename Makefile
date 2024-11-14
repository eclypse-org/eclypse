.DEFAULT_GOAL := check

check:
	pre-commit run -a

changelog:
	cz bump --changelog

setup:
	python -m pip install --upgrade pip
	pip install poetry
	poetry install --with=dev,deploy --no-root

isort:
	pycln --config=pyproject.toml eclypse
	isort eclypse
