# IO round trip

This example focuses on the [eclypse.io][eclypse.io] package. It is not a simulation
scenario. Instead, it shows how ECLYPSE graph objects can move between external
files and the in-memory [Application][eclypse.graph.application.Application] and
[Infrastructure][eclypse.graph.infrastructure.Infrastructure] classes.

Use it when you want to inspect the default importers and exporters side by
side, compare what each format preserves, or create a starting point for your
own graph exchange workflow.

The full code lives in the
[examples/io_round_trip](https://github.com/eclypse-org/eclypse/tree/main/examples/io_round_trip)
directory.

Run it from the repository root with:

```bash
uv run python -m examples.io_round_trip.main
```

## What it shows

The example ships small input files under `examples/io_round_trip/input` and
loads each one with the matching default importer:

- application inputs: ECLYPSE JSON, Docker Compose, GML, GraphML, node-link JSON,
  and TOSCA
- infrastructure inputs: ECLYPSE JSON, GML, GraphML, node-link JSON, and TOSCA

Each loaded graph is then exported to every compatible default output format.
Docker Compose is only available for applications, so the grid contains:

- `6 x 6` application conversions
- `5 x 5` infrastructure conversions
- `61` generated output files in total

The generated files are written under `examples/io_round_trip/output` using a
path that makes each conversion explicit:

```text
output/<kind>/from-<input-format>/to-<output-format>.<ext>
```

For example:

```text
output/application/from-gml/to-tosca.yaml
output/application/from-eclypse_json/to-docker_compose.yaml
output/infrastructure/from-graphml/to-node_link_json.json
output/infrastructure/from-tosca/to-eclypse_json.json
```

The example also writes `output/manifest.json` with one row per generated
conversion.

## Input cases

The input cases are declared once and reused by the grid runner. The case name
is the input format in snake case, while the parent folder carries the graph
kind.

??? example "Input case definitions"

    ```python
    --8<-- "examples/io_round_trip/cases.py"
    ```

## Conversion grid

The grid does the same thing for every case:

1. load the source file through [load_application][eclypse.io.load_application] or
   [load_infrastructure][eclypse.io.load_infrastructure]
2. ask [default_registry][eclypse.io.default_registry] for compatible output formats
3. dump the loaded graph through [dump_application][eclypse.io.dump_application] or
   [dump_infrastructure][eclypse.io.dump_infrastructure]

The example uses only default importers and exporters. It does not register
custom handlers.

??? example "Grid code"

    ```python
    --8<-- "examples/io_round_trip/grid.py"
    ```

## Entrypoint

The entrypoint runs the grid, writes the manifest, and prints a short summary of
the available formats and generated files.

??? example "Entrypoint code"

    ```python
    --8<-- "examples/io_round_trip/main.py"
    ```

## What to inspect

Start from `output/manifest.json` to see the full conversion matrix. Then
compare the outputs for the same input format, for example
`output/application/from-tosca` or `output/infrastructure/from-graphml`.

The canonical ECLYPSE JSON output is the most complete round-trip format. Graph
formats such as GML, GraphML, and node-link JSON are useful for graph tooling and
topology exchange. Docker Compose and TOSCA show how ECLYPSE applications and
infrastructures can be projected into cloud-edge oriented formats.

Related concepts:

- [Import and Export](../concepts/import-export.md)
- [Application][eclypse.graph.application.Application]
- [Infrastructure][eclypse.graph.infrastructure.Infrastructure]
- [eclypse.io][eclypse.io]
