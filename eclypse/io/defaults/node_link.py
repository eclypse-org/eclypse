"""NetworkX node-link JSON importers and exporters for ECLYPSE graphs."""

from __future__ import annotations

import json
from pathlib import Path
from typing import TYPE_CHECKING

from networkx.readwrite import json_graph

from eclypse.io.defaults.networkx import (
    NetworkXExporter,
    NetworkXImporter,
)

if TYPE_CHECKING:
    import networkx as nx

    from eclypse.graph import AssetGraph
    from eclypse.io.context import IOContext


class NodeLinkExporter(NetworkXExporter):
    """Exporter for NetworkX node-link JSON files."""

    def write_data(
        self,
        data: AssetGraph,
        target: str | Path,
        *,
        context: IOContext | None = None,  # noqa: ARG002
    ) -> None:
        """Write a NetworkX graph to node-link JSON.

        Args:
            data (AssetGraph): The graph to write.
            target (str | Path): The target JSON path.
            context (IOContext | None): Optional import/export customisation.
        """
        with Path(target).open("w", encoding="utf-8") as handle:
            json.dump(
                json_graph.node_link_data(self.networkx_graph(data), edges="edges"),
                handle,
                indent=2,
            )


class NodeLinkImporter(NetworkXImporter):
    """Importer for NetworkX node-link JSON files."""

    def read_data(
        self,
        source: str | Path,
        *,
        context: IOContext | None = None,  # noqa: ARG002
    ) -> nx.DiGraph:
        """Read a NetworkX graph from node-link JSON.

        Args:
            source (str | Path): The source JSON path.
            context (IOContext | None): Optional import/export customisation.

        Returns:
            nx.DiGraph: The decoded graph.
        """
        with Path(source).open(encoding="utf-8") as handle:
            return json_graph.node_link_graph(json.load(handle), edges="edges")
