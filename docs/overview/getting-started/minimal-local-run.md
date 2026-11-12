# Run a local simulation

This page shows the shortest path to a first successful ECLYPSE run.

We will:

1. create an infrastructure with a built-in builder,
2. create an application with a built-in builder,
3. configure a local simulation,
4. run it and inspect the report.

This path uses only local simulation components. No remote services or
communication interfaces are required.

## Build the scenario

The following example uses:

- [get_hierarchical][eclypse.builders.infrastructure.get_hierarchical] to build a
  small infrastructure,
- [get_sock_shop][eclypse.builders.application.sock_shop.application.get_sock_shop] to
  build a reference application,
- [RandomStrategy][eclypse.placement.strategies.RandomStrategy] for placement.

```python
from eclypse.builders.application import get_sock_shop
from eclypse.builders.infrastructure import get_hierarchical
from eclypse.placement.strategies import RandomStrategy
from eclypse.simulation import Simulation, SimulationConfig

seed = 22

infrastructure = get_hierarchical(
    n=20,
    include_default_assets=True,
    seed=seed,
)

application = get_sock_shop(
    include_default_assets=True,
    seed=seed,
)

config = SimulationConfig(
    seed=seed,
    max_steps=20,
    include_default_metrics=True,
    default_strategy=RandomStrategy(seed=seed),
)

simulation = Simulation(infrastructure, simulation_config=config)
simulation.register(application)
```

## Run the simulation

Once the infrastructure, application, and configuration are ready, start the
simulation and wait for it to finish:

```python
simulation.run()
```

## Inspect the report

After the run, the [report][eclypse.simulation.simulation.Simulation.report]
property exposes the collected data through the
[Report][eclypse.report.report.Report] interface:

```python
application_frame = simulation.report.application()
service_frame = simulation.report.service()

print(application_frame.head())
print(service_frame.head())
```

The exact object type depends on the selected report backend. By default,
ECLYPSE uses the backend configured in
[SimulationConfig][eclypse.simulation.config.SimulationConfig].

!!! note "See also"

    - [Inspect the results](inspect-results.md)
    - [Infrastructure and Application(s)](../concepts/topology.md)
    - [Simulation configuration](../concepts/simulation-configuration.md)

!!! note

    Looking for a larger runnable example? See the [Echo](../examples/echo.md) and
    [SockShop](../examples/sock_shop.md) pages.
