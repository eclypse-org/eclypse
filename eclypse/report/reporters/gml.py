# pylint: disable=unused-argument
"""Module for GMLReporter class.

It is used to report the simulation metrics in a GML format.
"""

from __future__ import annotations

from pathlib import Path
from typing import (
    TYPE_CHECKING,
    List,
)

import networkx as nx
from eclypse_core.report.reporter import Reporter

if TYPE_CHECKING:
    from eclypse_core.workflow.callbacks import EclypseCallback


class GMLReporter(Reporter):
    """Class to report the simulation metrics in a GML format.

    It uses `networkx.write_gml` method to write the graph on a file.
    """

    def report(
        self,
        event_name: str,
        event_idx: int,
        executed: List[EclypseCallback],
        *args,
        **kwargs,
    ):
        """Reports the callback values in a GML file.

        Args:
            event_name (str): The name of the event.
            event_idx (int): The index of the event trigger (tick).
            executed (List[EclypseCallback]): The executed callbacks.
        """
        for callback in executed:
            if callback.type is None:
                continue
            path = Path(self.report_path) / "gml"
            path.mkdir(parents=True, exist_ok=True)

            for d in self.dfs_data(callback.data):
                if d[-1] is None:
                    continue
                if not isinstance(d[-1], nx.DiGraph):
                    continue
                graph = d[-1]
                name = f"{callback.name}{'-'+graph.id if hasattr(graph, 'id') else ''}"
                path = path / f"{name}.gml"
                nx.write_gml(graph, path, stringizer=str)
