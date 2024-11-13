# Contributing Guidelines

We're glad you're considering contributing to ECLYPSE. Before you proceed, please take a moment to review the guidelines below to ensure a smooth contribution process.

## Table of Contents

- [Pull Requests](#pull-requests)
- [Conventional Commits](#conventional-commits)
- [Code Formatting](#code-formatting)
- [Linting](#linting)
- [Docstring Checks](#docstring-checks)
- [Pre-commit Hooks](#pre-commit-hooks)

## Pull Requests

To contribute to this project, follow these steps:

1. **Fork the repository:** Click the "Fork" button on the top right corner of this page. This will create a copy of the repository in your GitHub account.

2. **Clone the repository:** Clone your forked repository to your local machine. Replace `<your-username>` with your GitHub username.

    ```bash
    git clone https://github.com/<your-username>/eclypse.git
    ```

3. **Create a new branch:** Create a new branch for your changes. Use a descriptive name that reflects the nature of your work.

    ```bash
    git checkout -b feat/my-feature
    ```

4. **Make your changes:** Implement your changes and ensure they adhere to the guidelines outlined below.

5. **Commit your changes:** Commit your changes following the [conventional commits format](https://www.conventionalcommits.org/en/v1.0.0/).

    ```bash
    git add .
    git commit -m "feat: New feature short description"
    ```

6. **Push your changes:** Push your changes to your forked repository.

    ```bash
    git push origin feat/my-feature
    ```

7. **Submit a pull request:** Go to the GitHub page of your forked repository. You should see a "Compare & pull request" button. Click on it to open a pull request. Fill in the necessary information and submit the pull request.

## Conventional Commits

We enforce the usage of conventional commits in this repository. Please ensure that your commit messages follow the conventional commits format. You can find more information about conventional commits [here](https://www.conventionalcommits.org/en/v1.0.0/).

## Code Formatting

We use the following tools for code formatting:
- [Black](https://github.com/psf/black): Python code formatter.
- [isort](https://github.com/PyCQA/isort): Python import sorter.
- [docformatter](https://github.com/PyCQA/docformatter): Docstring formatter.

Please make sure that your code adheres to these formatting standards before submitting a pull request.

## Linting

We utilize the following tools for linting:
- [pycln](https://github.com/hadialqattan/pycln): Cleaner for Python code. It removes unused imports and unused variables.
- [mypy](https://github.com/python/mypy): Static type checker for Python.
- [pylint](https://github.com/pylint-dev/pylint): Python code quality checker.

Ensure that your code passes linting checks without any errors or warnings.

## Docstring Checks

We maintain high-quality docstrings in our codebase. To ensure consistency and correctness, we have a `check` makefile rule under `docs/Makefile` that exploits `pylint` with enablers for docstrings (C0114, C0115, C0116).

Please run the docstring check before submitting your changes to ensure that your docstrings meet our standards. You can execute the following command from the root directory of the repository:

```bash
cd docs
make check
```

## Pre-commit Hooks
Apart from docstring checks, we provide pre-commit hooks to automate the process of enforcing code formatting, linting, and other checks mentioned above. Follow the steps below to install and run the pre-commit hooks:

2. **Install pre-commit hooks:** Once pre-commit is installed, navigate to the root directory of the repository and run the following command:

    ```bash
    pre-commit install
    ```

    This will set up pre-commit hooks for your local repository.

3. **Run pre-commit checks:** You can now run all pre-commit checks on your changes before committing them. Use the following command:

    ```bash
    pre-commit run --all-files
    ```

    You can also use the Makefile rule `check` to run the pre-commit checks:

    ```bash
    make check
    ```

    This command will execute all pre-commit hooks on all files in your repository. Any issues found will be reported, and you'll need to address them before committing your changes.

By following these steps, you can ensure that your changes adhere to our coding standards and guidelines before committing them. If you encounter any issues or have questions about the pre-commit setup, feel free to reach out to us for assistance.
