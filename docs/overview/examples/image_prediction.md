# Image prediction

The image prediction example shows a remote application with trainer,
predictor, and end-user services. It combines service implementations, custom
metrics, and a degradation policy in emulation mode.

Use it when you want to understand:

- how to attach concrete service implementations to an application,
- how to configure a remote simulation,
- how to collect custom metrics from remote service behaviour.

The full code lives in the
[examples/image_prediction](https://github.com/eclypse-org/eclypse/tree/main/examples/image_prediction)
directory.

Run it from the repository root with:

```bash
uv run --with-requirements examples/image_prediction/requirements.txt python -m examples.image_prediction.main
```

## Application

??? example "Application code"

    ```python
    --8<-- "examples/image_prediction/application.py"
    ```

## Simulation

??? example "Simulation code"

    ```python
    --8<-- "examples/image_prediction/main.py"
    ```

## Metrics

??? example "Metrics code"

    ```python
    --8<-- "examples/image_prediction/metrics.py"
    ```

## What to inspect

This example is useful when the application behaviour matters, not only the
placement. Inspect the custom metrics together with the service implementations
to see how emulated runtime state becomes reportable simulation data.

Related concepts:

- [Emulation](../advanced/emulation/emulation.md)
- [Reporting](../advanced/reporting.md)
