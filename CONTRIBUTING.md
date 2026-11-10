# Contributing Guidelines

Contributions, bug reports, and feature requests are welcome.

## Reporting bugs and requesting features

Check [existing issues](https://github.com/eclypse-org/eclypse/issues) before opening a new one. Use the appropriate template:

- [Report a bug](https://github.com/eclypse-org/eclypse/issues/new?template=bug-report.md) ([template source](.github/ISSUE_TEMPLATE/bug-report.md)): include your environment, ECLYPSE version, a minimal reproducer, expected behaviour, and error output.
- [Request a feature](https://github.com/eclypse-org/eclypse/issues/new?template=feature-request.md) ([template source](.github/ISSUE_TEMPLATE/feature-request.md)): describe the problem, proposed behaviour, and alternatives considered.

For substantial changes, discuss the approach in an issue before implementing it.

## Dev Containers

This repository supports Dev Containers through the checked-in
[`/.devcontainer`](.devcontainer)
configuration.

If you use VS Code Dev Containers or GitHub Codespaces, you can rely on that
setup for a reproducible contributor environment.

## Setup

The project requires **Python `>=3.11,<3.15`** and uses [uv](https://docs.astral.sh/uv/). Fork and clone the repository, then run from the checkout:

```bash
cd eclypse
make setup
uv run pre-commit install
```

`make setup` installs the package and all development, test, and documentation dependencies in `.venv`, using `uv.lock`. Installing pre-commit enables the configured `pre-commit`, `commit-msg`, and `pre-push` hooks. The Dev Container setup runs both commands automatically.

## Pull Requests

1. Create a branch for your change.
2. Make the change and add or update tests for changed behaviour. Update documentation and examples when public behaviour changes.
3. Run the relevant tests and `make check`; run `make docs` when changing documentation or public API docstrings.
4. Commit your changes, push your branch, and open a pull request against `main`.

Explain the problem, resulting behaviour, and checks performed in the pull request. Link related issues, using `Closes #123` when the change resolves one.

## Conventional Commits

We enforce the usage of conventional commits in this repository. Please ensure that your commit messages follow the conventional commits format. You can find more information about conventional commits [here](https://www.conventionalcommits.org/en/v1.0.0/).

## Testing

We use `pytest` for the test suite.

Run the full suite:

```bash
uv run pytest
```

For a focused check, pass a test path, for example:

```bash
uv run pytest tests/unit/simulation/test_config.py
```

## Documentation

The documentation is built with Sphinx, treating warnings as errors:

```bash
make docs
```

The pages are written to `docs/_build/html`. To find classes missing from the documentation, run:

```bash
uv run --group docs make -C docs coverage
```

## Pre-commit Hooks

The configured pre-commit hooks check formatting, linting, types, and basic file hygiene:

- [Ruff](https://github.com/astral-sh/ruff): linting (rules in the `[tool.ruff]` section of `pyproject.toml`) and formatting.
- [isort](https://github.com/PyCQA/isort): import sorting.
- [mypy](https://mypy-lang.org/): type checking of the `eclypse` package.

After installing the hooks during setup, run all file checks with:

```bash
make check
```

Some hooks modify files automatically. Review those changes and rerun the checks. Commit-message checks run at commit time, and the branch commit check runs before pushing.

## Releasing (maintainers only)

Releases are made by maintainers, who can push to `main` and create tags.

1. On an up-to-date `main`, run:

    ```bash
    make bump
    ```

    Commitizen picks the next version from the commits since the last tag (`fix` → patch, `feat` → minor, breaking change → major; `make patch` forces a patch), updates the version in `pyproject.toml`, `uv.lock`, `eclypse/__init__.py` and `CITATION.cff`, adds the release to `CHANGELOG.md`, commits it as `chore(release): bump version X → Y` and creates the tag.

2. Push the commit and the tag:

    ```bash
    git push --follow-tags
    ```

3. The tag starts the `Build and Deploy to PyPI` workflow. It builds and checks the wheel, runs the pre-commit hooks, the tests and the quick examples, then publishes to PyPI through trusted publishing (`pypi` environment) and creates the GitHub Release with the changelog and the wheel.

If the workflow fails before publishing, fix the problem on `main` and release the next patch version. A version published to PyPI can never be replaced: a broken release is fixed by a new patch release, and can be yanked on PyPI so that it is no longer installed by default.
