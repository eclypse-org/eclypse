# Off-the-shelf

This example shows a complete local simulation built only from reusable ECLYPSE
components:

- the [get_hotel_reservation][eclypse.builders.application.get_hotel_reservation] application builder
- an infrastructure builder from [eclypse.builders.infrastructure][eclypse.builders.infrastructure]
- built-in update policies from [eclypse.policies][eclypse.policies]
- a built-in placement strategy

Use it when you want a minimal reference for composing existing building blocks
without writing custom services, topologies, or policy callables.

The full code lives in the
[examples/off_the_shelf](https://github.com/eclypse-org/eclypse/tree/main/examples/off_the_shelf)
directory.

Run it from the repository root with:

```bash
uv run python -m examples.off_the_shelf.main
```

## Application

The application is the built-in hotel reservation graph, paired with built-in
uniform-distribution and degradation policies that progressively make
placement harder.

ECLYPSE also provides several other ready-made application builders collected
in [eclypse.builders.application][eclypse.builders.application].

??? example "Application code"

    ```python
    --8<-- "examples/off_the_shelf/application.py"
    ```

## Infrastructure

The infrastructure is a generated hierarchical topology using the default
assets and a built-in policy mix for flapping availability, uniform
perturbations, periodic latency spikes, and scheduled degradation. ECLYPSE also
provides several other off-the-shelf infrastructure builders collected in
[eclypse.builders.infrastructure][eclypse.builders.infrastructure]. Together with `BestFitStrategy`, this
example exercises repeated placement under a changing environment.

??? example "Infrastructure code"

    ```python
    --8<-- "examples/off_the_shelf/infrastructure.py"
    ```

## Simulation

The simulation registers the built-in application on the generated
infrastructure with a built-in placement strategy and runs it locally.

??? example "Simulation code"

    ```python
    --8<-- "examples/off_the_shelf/main.py"
    ```

## What to inspect

This example is the quickest template for a local experiment built from
existing components. Inspect placement changes and application-level metrics as
the infrastructure policies make resources less stable.

Related concepts:

- [Builders](../concepts/builders.md)
- [Update policies](../concepts/update-policy.md)
- [Placement Strategy](../concepts/placement-strategy.md)
