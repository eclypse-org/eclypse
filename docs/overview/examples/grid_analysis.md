# Grid analysis

The grid analysis example runs a Ray Tune sweep over infrastructure topology,
load, failure policy, random seed, and placement strategy choices.

Use it when you want to understand:

- how to wrap an ECLYPSE simulation in a parameter-search function,
- how to compare placement strategies across many generated infrastructures,
- how to write custom infrastructure assets and policies for experiments.

The full code lives in the
[examples/grid_analysis](https://github.com/eclypse-org/eclypse/tree/main/examples/grid_analysis)
directory.

Run it from the repository root with:

```bash
uv run --with-requirements examples/grid_analysis/requirements.txt python -m examples.grid_analysis.main
```

## Simulation sweep

??? example "Main sweep code"

    ```python
    --8<-- "examples/grid_analysis/main.py"
    ```

## Infrastructure

??? example "Infrastructure code"

    ```python
    --8<-- "examples/grid_analysis/infrastructure.py"
    ```

## Placement strategy

??? example "Strategy code"

    ```python
    --8<-- "examples/grid_analysis/strategy.py"
    ```

## What to inspect

Use this example as a template for repeated experiments. The main result is not
a single simulation trace, but a grid of runs that lets you compare placement
strategies and infrastructure choices under the same sweep logic.

Related concepts:

- [Placement Strategy](../concepts/placement-strategy.md)
- [Update policies](../concepts/update-policy.md)
