"""JSON importers and exporters for canonical ECLYPSE graph data."""

from __future__ import annotations

import json
from pathlib import Path
from typing import (
    TYPE_CHECKING,
    Any,
)

from eclypse.io.graphs import (
    ECLYPSEDataExporter,
    ECLYPSEDataImporter,
)

if TYPE_CHECKING:
    from eclypse.io.context import IOContext


class JSONExporter(ECLYPSEDataExporter):
    """Exporter for canonical ECLYPSE JSON files."""

    def write_data(
        self,
        data: dict[str, Any],
        target: str | Path,
        *,
        context: IOContext | None = None,  # noqa: ARG002
    ) -> None:
        """Write canonical graph data to a JSON file.

        Args:
            data (dict[str, Any]): The graph data to write.
            target (str | Path): The target JSON path.
            context (IOContext | None): Optional import/export customisation.
        """
        with Path(target).open("w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2, sort_keys=True)


class JSONImporter(ECLYPSEDataImporter):
    """Importer for canonical ECLYPSE JSON files."""

    def read_data(
        self,
        source: str | Path,
        *,
        context: IOContext | None = None,  # noqa: ARG002
    ) -> dict[str, Any]:
        """Read canonical graph data from a JSON file.

        Args:
            source (str | Path): The JSON source path.
            context (IOContext | None): Optional import/export customisation.

        Returns:
            dict[str, Any]: The decoded graph data.
        """
        with Path(source).open(encoding="utf-8") as handle:
            return json.load(handle)
