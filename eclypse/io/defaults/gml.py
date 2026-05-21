"""GML importers and exporters for ECLYPSE graphs."""

from __future__ import annotations

from typing import TYPE_CHECKING

import networkx as nx

from eclypse.io.defaults.networkx import (
    NetworkXExporter,
    NetworkXImporter,
)

if TYPE_CHECKING:
    from pathlib import Path

    from eclypse.graph import AssetGraph
    from eclypse.io.context import IOContext


class GMLExporter(NetworkXExporter):
    """Exporter for GML files."""

    def write_data(
        self,
        data: AssetGraph,
        target: str | Path,
        *,
        context: IOContext | None = None,  # noqa: ARG002
    ) -> None:
        """Write a NetworkX graph to a GML file.

        Args:
            data (AssetGraph): The graph to write.
            target (str | Path): The target GML path.
            context (IOContext | None): Optional import/export customisation.
        """
        nx.write_gml(self.networkx_graph(data), target, stringizer=str)


class GMLImporter(NetworkXImporter):
    """Importer for GML files."""

    def read_data(
        self,
        source: str | Path,
        *,
        context: IOContext | None = None,  # noqa: ARG002
    ) -> nx.DiGraph:
        """Read a NetworkX graph from a GML file.

        Args:
            source (str | Path): The source GML path.
            context (IOContext | None): Optional import/export customisation.

        Returns:
            nx.DiGraph: The decoded graph.
        """
        return nx.read_gml(source)
