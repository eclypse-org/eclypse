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

- [Ruff](https://github.com/astral-sh/ruff): for linting and formatting Python code.
- [isort](https://github.com/PyCQA/isort): for sorting and organizing Python imports (*Ruff could also handle this, but we use some standards that are not already ported to Ruff*).

Please make sure that your code adheres to these formatting standards before submitting a pull request.
You can check and format your code automatically with:

```bash
isort eclypse
ruff check
ruff format
```

## Linting

Linting in this project is handled entirely by [Ruff](https://github.com/astral-sh/ruff).

Ruff is an extremely fast Python linter and formatter that replaces multiple traditional tools (such as flake8, pycodestyle, pyflakes, pydocstyle, and others) with a single, unified command-line interface.

Before submitting your pull request, ensure that your code passes all linting checks defined in the `.ruff.toml` file, by running:

```bash
ruff check
```

If you want Ruff to automatically fix all fixable issues, you can run:

```bash
ruff check --fix
```

Ruff will detect and correct most common style, import, and docstring issues automatically.
Please make sure that all warnings and errors are resolved before committing your changes.

## Pre-commit Hooks

We provide pre-commit hooks to automate formatting and linting checks. Follow the steps below to install and run them:

1. **Install pre-commit:**

    ```bash
    pip install pre-commit
    ```

2. **Install the hooks:**

    ```bash
    pre-commit install
    ```

3. **Run pre-commit checks manually (optional):**

    ```bash
    pre-commit run -a
    ```

    Alternatively, you can use the Makefile rule:

    ```bash
    make check
    ```

This will execute all pre-commit hooks (formatting and linting) across your repository. Any issues found will be reported, and you'll need to address them before committing your changes.

By following these steps, you ensure that your contributions maintain consistency and quality across the codebase. If you encounter any issues or have questions about the setup, feel free to reach out for assistance.
