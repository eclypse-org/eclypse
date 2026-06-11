"""Run the default ECLYPSE IO importer/exporter conversion grid."""

from __future__ import annotations

from eclypse.io import default_registry

from .cases import (
    INPUT_CASES,
    OUTPUT_DIR,
)
from .grid import (
    run_grid,
    write_manifest,
)


def main() -> None:
    """Load every example input and export it to every compatible format."""
    rows = run_grid(INPUT_CASES)
    write_manifest(rows)

    print("Application formats:", default_registry.formats("application"))
    print("Infrastructure formats:", default_registry.formats("infrastructure"))
    print("Inputs converted:", len(INPUT_CASES))
    print("Outputs written:", len(rows))
    print("Output directory:", OUTPUT_DIR)


if __name__ == "__main__":
    main()
