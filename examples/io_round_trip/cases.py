"""Input cases and format metadata for the IO round-trip example."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from eclypse.io import (
    ApplicationContext,
    DockerComposeContext,
    InfrastructureContext,
    TOSCAApplicationContext,
    TOSCAInfrastructureContext,
)
from eclypse.utils.types import GraphKind

ROOT = Path(__file__).resolve().parent
INPUT_DIR = ROOT / "input"
OUTPUT_DIR = ROOT / "output"
SEED = 42

OUTPUT_EXTENSIONS = {
    "docker-compose": "yaml",
    "eclypse-json": "json",
    "gml": "gml",
    "graphml": "graphml",
    "node-link-json": "json",
    "tosca": "yaml",
}


@dataclass(frozen=True, slots=True)
class IOCase:
    """Input case handled by the IO grid.

    Args:
        name (str): Stable input case name used for output folders.
        kind (GraphKind): Graph kind expected from the importer.
        format (str): Built-in IO format name.
        path (Path): Input path.
    """

    name: str
    kind: GraphKind
    format: str
    path: Path


INPUT_CASE_SPECS = {
    "application": {
        "eclypse-json": "eclypse.json",
        "docker-compose": "docker-compose.yaml",
        "gml": "gml.gml",
        "graphml": "graphml.graphml",
        "node-link-json": "node-link.json",
        "tosca": "tosca.yaml",
    },
    "infrastructure": {
        "eclypse-json": "eclypse.json",
        "gml": "gml.gml",
        "graphml": "graphml.graphml",
        "node-link-json": "node-link.json",
        "tosca": "tosca.yaml",
    },
}

INPUT_CASES = [
    IOCase(
        format_.replace("-", "_"),
        kind,
        format_,
        INPUT_DIR / kind / filename,
    )
    for kind, formats in INPUT_CASE_SPECS.items()
    for format_, filename in formats.items()
]


def context_for(kind: GraphKind, format: str, *, direction: str):
    """Return an IO context suitable for an example conversion.

    Args:
        kind (GraphKind): Graph kind being imported or exported.
        format (str): Built-in IO format name.
        direction (str): Either ``"import"`` or ``"export"``.

    Returns:
        ApplicationContext | InfrastructureContext: Format-aware IO context.
    """
    if kind == "application":
        if format == "docker-compose":
            return DockerComposeContext(
                strict=False,
                seed=SEED,
                allow_image_fallback_to_node=direction == "export",
            )
        if format == "tosca":
            return TOSCAApplicationContext(strict=False, seed=SEED)
        return ApplicationContext(strict=False, seed=SEED)

    if format == "tosca":
        return TOSCAInfrastructureContext(strict=False, seed=SEED)
    return InfrastructureContext(strict=False, seed=SEED)
