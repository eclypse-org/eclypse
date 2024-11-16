# Documentation

Documentation is built with sphinx.

Build the documentation (it must be executed in the `docs` folder):
```
sphinx-build . _build
```

### Doc coverage
it is possible to check the class coverage to find classes that are missing from the documentation using the command:
```
sphinx-build -b coverage . _build
```
