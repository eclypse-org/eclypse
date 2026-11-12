# Simulation configuration

The simulation represents the environment where you can deploy and emulate your
application on the given infrastructure.

After you [define your application(s) and infrastructure](topology.md), a
simulation run is controlled through
[SimulationConfig][eclypse.simulation.config.SimulationConfig].

At a high level, the configuration answers four questions:

- how the run advances and stops,
- which events and metrics are included,
- how logs and reports are written,
- whether execution is local or remote.

## Typical workflow

The usual flow is:

1. create a [SimulationConfig][eclypse.simulation.config.SimulationConfig],
2. create a [Simulation][eclypse.simulation.simulation.Simulation],
3. register one or more applications with a placement strategy,
4. run the simulation and wait for completion.

```python
from eclypse.placement.strategies import RandomStrategy
from eclypse.simulation import Simulation, SimulationConfig

config = SimulationConfig(
    max_steps=50,
    include_default_metrics=True,
    report_format="parquet",
    report_backend="polars",
    path="my-simulation",
    seed=42,
)

simulation = Simulation(example_infra, config)
simulation.register(example_app, RandomStrategy(seed=42))

simulation.run()

application_frame = simulation.report.application()
```

## Configuration reference

The table below summarises every public parameter of
[SimulationConfig][eclypse.simulation.config.SimulationConfig].

| Parameter | Default | Meaning |
| --- | --- | --- |
| `step_every_ms` | `"auto"` | Controls how the driving `enact` event is scheduled. Use `"auto"` for continuous local progression, `"manual"` or `None` for fully manual stepping, or a numeric value for a fixed periodic step. In remote mode, `"auto"` resolves to manual stepping unless a numeric cadence is provided. |
| `timeout` | `None` | Stops the simulation after the given number of seconds. |
| `max_steps` | `None` | Stops the simulation after the given number of driving-event triggers. |
| `reporters` | `None` | Additional reporter classes to merge with the built-in reporter set. This is mainly useful when writing custom reporting sinks. |
| `events` | `None` | Explicit event list for the simulation. Default lifecycle events are still added automatically when missing. |
| `include_default_metrics` | `False` | Adds the built-in metrics shipped by ECLYPSE to the event set. |
| `default_strategy` | `None` | Placement strategy used for applications registered without an explicit strategy. Per-application strategies passed to [register][eclypse.simulation.simulation.Simulation.register] take precedence. |
| `seed` | random | Seed used for deterministic sampling and reproducible scenarios. |
| `path` | default simulation path | Output directory used for logs, reports, and `config.json`. |
| `log_to_file` | `False` | If enabled, runtime logs are also written to the simulation output path. |
| `log_level` | `"ECLYPSE"` | Minimum log level used by the runtime logger. |
| `report_chunk_size` | `100` | Number of report entries buffered before each reporter flush. |
| `report_format` | `"csv"` | On-disk report format. Built-in options are `"csv"`, `"json"`, and `"parquet"`. |
| `report_backend` | `"pandas"` | Dataframe backend used when querying reports through [Report][eclypse.report.report.Report]. |
| `remote` | `False` | Enables emulation mode. It can be a boolean or a [RemoteBootstrap][eclypse.remote.bootstrap.bootstrap.RemoteBootstrap] instance for custom remote cluster setup. |

### Timing and stopping

Use `step_every_ms`, `timeout`, and `max_steps` together to control how a
run advances and when it stops.

```python
config = SimulationConfig(
    step_every_ms=500,
    timeout=60,
    max_steps=120,
)
```

This configuration asks the simulation to:

- progress every half second,
- stop after one minute,
- or stop earlier if 120 steps are reached first.

If you want manual progression instead, opt in explicitly:

```python
config = SimulationConfig(step_every_ms=None)
```

and then advance the run explicitly with
[step][eclypse.simulation.simulation.Simulation.step].

### Events and metrics

By default, you can supply your own event list through `events` and decide
whether to include the built-in metrics:

```python
from eclypse.report.metrics.defaults import get_default_metrics

config = SimulationConfig(
    events=[my_event, my_callback, my_metric],
    include_default_metrics=False,
)
```

If you prefer the default metrics as a starting point:

```python
config = SimulationConfig(include_default_metrics=True)
```

For more on event roles and event types, see [Events](events.md).

### Logging and output paths

The output path and logging parameters are useful when you want reproducible,
inspectable runs:

```python
config = SimulationConfig(
    path="runs/baseline-a",
    log_level="INFO",
    log_to_file=True,
    seed=42,
)
```

!!! tip

    ECLYPSE uses [Loguru](https://loguru.readthedocs.io/) under the hood for
    logging. It preserves the standard levels (`DEBUG`, `INFO`,
    `WARNING`, etc.) and adds `ECLYPSE` between `DEBUG` and `INFO` for
    framework-specific runtime messages.

### Reporting

Two parameters shape the reporting workflow:

- `report_format` controls what is written to disk,
- `report_backend` controls what kind of frame object you get back later.

```python
config = SimulationConfig(
    report_format="parquet",
    report_backend="polars_lazy",
    report_chunk_size=500,
    include_default_metrics=True,
)
```

This is a good fit for larger runs where you want efficient on-disk storage and
lazy analytical queries afterwards.

See also:

- [Inspect the results](../getting-started/inspect-results.md)
- [Reporting](../advanced/reporting.md)

### Remote execution

Set `remote=True` to enable the default emulation bootstrap:

```python
config = SimulationConfig(remote=True)
```

If you need more control, pass a
[RemoteBootstrap][eclypse.remote.bootstrap.bootstrap.RemoteBootstrap] instance:

```python
from eclypse.remote.bootstrap import RemoteBootstrap

bootstrap = RemoteBootstrap()
config = SimulationConfig(remote=bootstrap)
```

This is the entry point for running remote services over Ray. For the runtime
details, see [Emulation](../advanced/emulation/emulation.md).

## Using the configuration in a simulation

Once the configuration is ready, pass it to
[Simulation][eclypse.simulation.simulation.Simulation], then register your
applications together with a placement strategy:

```python
from eclypse.placement.strategies import RandomStrategy
from eclypse.simulation import Simulation

simulation = Simulation(example_infra, config)
simulation.register(example_app, RandomStrategy(seed=42))

simulation.run()
```

When the run finishes, the [report][eclypse.simulation.simulation.Simulation.report]
property exposes a [Report][eclypse.report.report.Report] object:

```python
application_frame = simulation.report.application()
generic_frame = simulation.report.frame("service")
```

!!! note

    Looking for complete runnable scenarios? See [Examples](../examples/index.md).
