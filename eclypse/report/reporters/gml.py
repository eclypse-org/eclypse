# pylint: disable=unused-argument
"""Module for GMLReporter class.

It is used to report the simulation metrics in GML format.
"""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    List,
)

import networkx as nx

from eclypse.report.reporter import Reporter

if TYPE_CHECKING:
    from eclypse.workflow.event import EclypseEvent


class GMLReporter(Reporter):
    """Class to report simulation metrics in GML format using NetworkX."""

    def __init__(self, *args, **kwargs):
        """Initialize the GML reporter."""
        super().__init__(*args, **kwargs)
        self.report_path = self.report_path / "gml"

    def report(
        self,
        _: str,
        __: int,
        callback: EclypseEvent,
    ) -> List[tuple[str, nx.DiGraph]]:
        """Extract graph data from callback and prepare it for writing.

        Args:
            _ (str): The name of the event.
            __ (int): The index of the event trigger (step).
            callback (EclypseEvent): The executed callback containing the data to report.

        Returns:
            List of (graph_name, graph_object) tuples.
        """
        entries = []
        for d in self.dfs_data(callback.data):
            if not d or d[-1] is None:
                continue
            graph = d[-1]
            if not isinstance(graph, nx.DiGraph):
                continue
            name = f"{callback.name}{'-' + graph.id if hasattr(graph, 'id') else ''}"
            entries.append((name, graph))
        return entries

    async def write(self, _: str, data: List[tuple[str, nx.DiGraph]]):
        """Write graphs in GML format.

        Args:
            callback_type (str): The type of the callback.
            data (List[Tuple[str, nx.DiGraph]]): The graphs to write.
        """
        for name, graph in data:
            path = self.report_path / f"{name}.gml"
            nx.write_gml(graph, path, stringizer=str)
