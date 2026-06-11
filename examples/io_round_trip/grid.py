"""Conversion grid for all default ECLYPSE IO formats."""

from __future__ import annotations

import json
from typing import Any

from eclypse.io import (
    default_registry,
    dump_application,
    dump_infrastructure,
    load_application,
    load_infrastructure,
)

from .cases import (
    OUTPUT_DIR,
    OUTPUT_EXTENSIONS,
    IOCase,
    context_for,
)


def load_case(case: IOCase):
    """Load one input case using the matching default importer.

    Args:
        case (IOCase): Input case to load.

    Returns:
        Application | Infrastructure: Loaded graph object.
    """
    context = context_for(case.kind, case.format, direction="import")
    if case.kind == "application":
        return load_application(
            case.path,
            using=case.format,
            application_context=context,
        )
    return load_infrastructure(
        case.path,
        using=case.format,
        infrastructure_context=context,
    )


def dump_case(graph, case: IOCase, output_format: str) -> dict[str, Any]:
    """Dump one loaded input to one output format.

    Args:
        graph (Application | Infrastructure): Graph object to export.
        case (IOCase): Source input case.
        output_format (str): Built-in output format name.

    Returns:
        dict[str, Any]: Manifest row for the generated output.
    """
    output_name = output_format.replace("-", "_")
    extension = OUTPUT_EXTENSIONS[output_format]
    target = (
        OUTPUT_DIR
        / case.kind
        / f"from-{case.name}"
        / f"to-{output_name}.{extension}"
    )
    target.parent.mkdir(parents=True, exist_ok=True)
    context = context_for(case.kind, output_format, direction="export")

    if case.kind == "application":
        dump_application(
            graph,
            target,
            using=output_format,
            application_context=context,
        )
    else:
        dump_infrastructure(
            graph,
            target,
            using=output_format,
            infrastructure_context=context,
        )

    return {
        "input": case.name,
        "kind": case.kind,
        "input_format": case.format,
        "output_format": output_format,
        "path": str(target.relative_to(OUTPUT_DIR)),
    }


def run_grid(cases: list[IOCase]) -> list[dict[str, Any]]:
    """Run all input cases through all compatible default exporters.

    Args:
        cases (list[IOCase]): Input cases to convert.

    Returns:
        list[dict[str, Any]]: Manifest rows for every generated output.
    """
    rows = []
    for case in cases:
        graph = load_case(case)
        for output_format in default_registry.formats(case.kind):
            rows.append(dump_case(graph, case, output_format))
    return rows


def write_manifest(rows: list[dict[str, Any]]) -> None:
    """Write a JSON manifest describing generated output files.

    Args:
        rows (list[dict[str, Any]]): Output rows produced by :func:`run_grid`.
    """
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    manifest = {
        "application_export_formats": default_registry.formats("application"),
        "infrastructure_export_formats": default_registry.formats("infrastructure"),
        "outputs": rows,
    }
    with (OUTPUT_DIR / "manifest.json").open("w", encoding="utf-8") as handle:
        json.dump(manifest, handle, indent=2, sort_keys=True)
