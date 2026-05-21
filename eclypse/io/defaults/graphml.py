"""GraphML importers and exporters for ECLYPSE graphs."""

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


class GraphMLExporter(NetworkXExporter):
    """Exporter for GraphML files."""

    def write_data(
        self,
        data: AssetGraph,
        target: str | Path,
        *,
        context: IOContext | None = None,  # noqa: ARG002
    ) -> None:
        """Write a NetworkX graph to a GraphML file.

        Args:
            data (AssetGraph): The graph to write.
            target (str | Path): The target GraphML path.
            context (IOContext | None): Optional import/export customisation.
        """
        nx.write_graphml(self.networkx_graph(data), target)


class GraphMLImporter(NetworkXImporter):
    """Importer for GraphML files."""

    def read_data(
        self,
        source: str | Path,
        *,
        context: IOContext | None = None,  # noqa: ARG002
    ) -> nx.DiGraph:
        """Read a NetworkX graph from a GraphML file.

        Args:
            source (str | Path): The source GraphML path.
            context (IOContext | None): Optional import/export customisation.

        Returns:
            nx.DiGraph: The decoded graph.
        """
        return nx.read_graphml(source)
