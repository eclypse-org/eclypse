# pylint: disable=unused-argument
"""Module for GMLReporter class.

It is used to report the simulation metrics in GML format.
"""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
)

import networkx as nx

from eclypse.report.reporter import Reporter
from eclypse.utils.defaults import GML_REPORT_DIR

if TYPE_CHECKING:
    from collections.abc import (
        Generator,
    )
    from pathlib import Path

    from eclypse.workflow.event import EclypseEvent


class GMLReporter(Reporter):
    """Class to report simulation metrics in GML format using NetworkX."""

    def __init__(self, report_path: str | Path):
        """Initialize the GML reporter."""
        super().__init__(report_path)
        self.report_path = self.report_path / GML_REPORT_DIR

    def report(
        self,
        _: str,
        __: int,
        callback: EclypseEvent,
    ) -> Generator[tuple[str, nx.DiGraph], None, None]:
        """Extract graph data from callback and prepare it for writing.

        Args:
            _ (str): The name of the event.
            __ (int): The index of the event trigger (step).
            callback (EclypseEvent):
                The executed callback containing the data to report.

        Returns:
            Generator[tuple[str, nx.DiGraph], None, None]:
                Graph entries to write lazily.
        """
        for d in self.callback_rows(callback):
            if not d or d[-1] is None:
                continue
            graph = d[-1]
            if not isinstance(graph, nx.DiGraph):
                continue
            name = f"{callback.name}{'-' + graph.id if hasattr(graph, 'id') else ''}"
            yield (name, graph)

    async def write(self, _: str, data: list[tuple[str, nx.DiGraph]]):
        """Write graphs in GML format.

        Args:
            callback_type (str): The type of the callback.
            data (list[tuple[str, nx.DiGraph]]): The graphs to write.
        """
        for name, graph in data:
            path = self.report_path / f"{name}.gml"
            nx.write_gml(graph, path, stringizer=str)
