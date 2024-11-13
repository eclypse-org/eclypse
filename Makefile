.DEFAULT_GOAL := check

check:
	pre-commit run -a

isort:
	pycln --config=pyproject.toml eclypse
	isort eclypse