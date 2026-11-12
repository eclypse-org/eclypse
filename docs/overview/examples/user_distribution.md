# User distribution

The user distribution example customises a generated infrastructure with a
`user_count` asset and updates latency and placement conditions as the user
distribution evolves.

Use it when you want to understand:

- how to add a custom infrastructure asset,
- how to write metrics around domain-specific infrastructure state,
- how update policies can drive a longer-running simulation.

The full code lives in the
[examples/user_distribution](https://github.com/eclypse-org/eclypse/tree/main/examples/user_distribution)
directory.

Run it from the repository root with:

```bash
uv run --with-requirements examples/user_distribution/requirements.txt python -m examples.user_distribution.main
```

## Infrastructure

??? example "Infrastructure code"

    ```python
    --8<-- "examples/user_distribution/infrastructure.py"
    ```

## Metrics

??? example "Metrics code"

    ```python
    --8<-- "examples/user_distribution/metric.py"
    ```

## Simulation

??? example "Simulation code"

    ```python
    --8<-- "examples/user_distribution/main.py"
    ```

## What to inspect

Use this example when the infrastructure has domain-specific state. The
`user_count` asset shows how custom node attributes can drive metrics and
update policies without changing the core simulator.

Related concepts:

- [Assets](../concepts/assets.md)
- [Update policies](../concepts/update-policy.md)
- [Reporting](../advanced/reporting.md)
