# Documentation

Documentation is built with sphinx.

Build the documentation from the repository root:
```
make docs
```

## Doc coverage
it is possible to check the class coverage to find classes that are missing from the documentation using the command (from the repository root):
```
uv run --group docs make -C docs coverage
```
