# Inspect the results

ECLYPSE stores simulation outputs on disk and exposes them through the
[Report][eclypse.report.report.Report] interface.

The report API gives you two main choices:

- the **report format**, which controls how data is written to disk,
- the **report backend**, which controls the dataframe implementation returned
  when you query the report.

## Choose the report format

Use the `report_format` parameter of
[SimulationConfig][eclypse.simulation.config.SimulationConfig] to choose how the raw data
is written:

- `"csv"`: easy to inspect manually,
- `"json"`: useful for structured debugging and integration,
- `"parquet"`: best suited to larger runs and analytical workloads.

```python
from eclypse.simulation import SimulationConfig

config = SimulationConfig(
    report_format="parquet",
    include_default_metrics=True,
)
```

## Choose the report backend

Use `report_backend` to control the in-memory dataframe implementation used
by [Report][eclypse.report.report.Report]:

- `"pandas"`
- `"polars"`
- `"polars_lazy"`

```python
config = SimulationConfig(
    report_backend="polars",
    report_format="parquet",
    include_default_metrics=True,
)
```

## Query report frames

Once a simulation has completed, you can retrieve report frames either through
the convenience methods or through the generic
[frame][eclypse.report.report.Report.frame] entry point:

```python
report = simulation.report

application_frame = report.application()
service_frame = report.service()
generic_frame = report.frame("interaction")
```

You can also restrict the data by report range:

```python
recent_steps = report.service(report_range=(10, 20))
```

## Standalone report loading

Reports can also be loaded later from disk:

```python
from eclypse.report import Report

report = Report("path/to/simulation")
frame = report.application()
```

If needed, you can explicitly set the format when loading:

```python
report = Report("path/to/simulation", report_format="parquet")
```

!!! note "See also"

    - [Simulation configuration](../concepts/simulation-configuration.md)
    - [Reporting](../advanced/reporting.md)
