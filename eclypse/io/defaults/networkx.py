"""Shared NetworkX-backed importer and exporter base classes."""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Generic,
)

import networkx as nx

from eclypse.graph import AssetGraph
from eclypse.io.base import (
    GraphExporter,
    GraphImporter,
)
from eclypse.io.graphs import (
    graph_from_networkx,
    graph_to_networkx,
)
from eclypse.utils.types import (
    TGraph,
)

if TYPE_CHECKING:
    from eclypse.io.context import IOContext
    from eclypse.utils.types import GraphKind


class NetworkXExporter(GraphExporter[TGraph, TGraph], Generic[TGraph]):
    """Base class for exporters that write through NetworkX graphs."""

    def to_data(
        self,
        graph: TGraph,
        *,
        context: IOContext | None = None,  # noqa: ARG002
    ) -> TGraph:
        """Return the graph object handled by NetworkX exporters.

        Args:
            graph (TGraph): The graph to export.
            context (IOContext | None): Optional import/export customisation.

        Returns:
            TGraph: The graph object to write.
        """
        return graph

    def networkx_graph(self, graph: AssetGraph) -> nx.DiGraph:
        """Return a NetworkX copy ready for file-format writers.

        Args:
            graph (AssetGraph): The ECLYPSE graph to convert.

        Returns:
            nx.DiGraph: A NetworkX copy carrying graph metadata.
        """
        return graph_to_networkx(graph)


class NetworkXImporter(GraphImporter[AssetGraph, nx.DiGraph]):
    """Base class for importers that read through NetworkX graphs."""

    def from_data(
        self,
        data: nx.DiGraph,
        *,
        kind: GraphKind | None = None,
        context: IOContext | None = None,
    ) -> AssetGraph:
        """Convert a NetworkX graph into an ECLYPSE graph.

        Args:
            data (nx.DiGraph): The NetworkX graph to convert.
            kind (GraphKind | None): Graph kind requested by the caller.
            context (IOContext | None): Optional import/export customisation.

        Returns:
            AssetGraph: The converted graph object.

        Raises:
            ValueError: If ``kind`` is not provided.
        """
        if kind is None:
            raise ValueError("NetworkX importers require an explicit graph kind.")
        return graph_from_networkx(data, kind=kind, context=context)
