# Install ECLYPSE

ECLYPSE can be installed from [PyPI](https://pypi.org/project/eclypse/).
It requires Python `>=3.11,<3.15`.

!!! note

    Do not use the global environment to install ECLYPSE.
    It is recommended to create a [virtual environment](https://docs.python.org/3/library/venv.html) first.

## Using pip

Create and activate a virtual environment, then install the package:

```shell
python -m venv .venv
source .venv/bin/activate
pip install eclypse
```

## Using uv

If your project uses [uv](https://docs.astral.sh/uv/), add ECLYPSE to the
project dependencies:

```shell
uv add eclypse
```

## Installing from source

For development, clone the repository and install the dependency groups you
need:

```shell
git clone https://github.com/eclypse-org/eclypse.git
cd eclypse
uv sync --group dev --group test
```

The documentation dependencies live in the `docs` group:

```shell
uv sync --group docs
```

Now you are ready to run [your first ECLYPSE simulation](getting-started/index.md)!
