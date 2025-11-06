"""Module for the PlacementView class.

It can be considered as a snapshot of the required resources of the infrastructure,
considering the current placements of application services.

It is used to check if the requirements of the placements can be satisfied by the
infrastructure, thus allowing the placement to be enacted.
"""

from __future__ import annotations

from collections import defaultdict
from functools import cached_property
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Set,
    Tuple,
)

import networkx as nx

from eclypse.graph import AssetGraph
from eclypse.graph.assets import (
    Concave,
    Convex,
)

if TYPE_CHECKING:
    from eclypse.graph import Infrastructure
    from eclypse.graph.assets import AssetBucket
    from eclypse.placement import Placement


class PlacementView(nx.DiGraph):
    """PlacementView is a snapshot of the required resources of an Infrastructure."""

    def __init__(self, infrastructure: Infrastructure):
        """Initializes the PlacementView."""
        super().__init__(graph_id="PlacementView")
        self.nodes_used_by: Dict[str, Set[str]] = defaultdict(set)
        self.infrastructure = infrastructure
        self.residual = self._get_snapshot()

    def get_node_view(self, node_name: str) -> Dict[str, Any]:
        """Gets the resources required on a node.

        Args:
            node_name (str): The name of the node.

        Returns:
            ServiceRequirements: The resources required on the node.
        """
        if self.has_node(node_name):
            return self.nodes[node_name]
        return self.infrastructure.node_assets.lower_bound

    def get_edge_view(self, source: str, target: str) -> Dict[Tuple[str, str], Any]:
        """Gets the resources required on a link.

        Args:
            source (str): The source node of the link.
            target (str): The target node of the link.

        Returns:
            S2SRequirements: The resources required on the link.
        """
        return self.get_edge_data(
            source, target, self.infrastructure.edge_assets.lower_bound
        )

    @cached_property
    def node_aggregate(self) -> Callable[..., Dict[str, Any]]:
        """Returns a function that aggregates the resources required on a node.

        Returns:
            Callable[..., Dict[str, Any]]: The function that aggregates the resources.
        """
        return self.infrastructure.node_assets.flip().aggregate

    @cached_property
    def edge_aggregate(self) -> Callable[..., Dict[str, Any]]:
        """Returns a function that aggregates the resources required on a link.

        Returns:
            Callable[..., Dict[str, Any]]: The function that aggregates the resources.
        """
        return self.infrastructure.edge_assets.flip().aggregate

    @property
    def node_assets(self) -> AssetBucket:
        """Alias for the node assets of the infrastructure.

        Returns:
            AssetBucket: The node assets of the infrastructure.
        """
        return self.infrastructure.node_assets

    @property
    def edge_assets(self) -> AssetBucket:
        """Alias for the edge assets of the infrastructure.

        Returns:
            AssetBucket: The edge assets of the infrastructure.
        """
        return self.infrastructure.edge_assets

    @cached_property
    def _concave_convex_assets(self):
        """Returns the concave and convex assets of the infrastructure.

        Returns:
            List[str]: The concave and convex assets of the infrastructure.
        """
        return [
            k
            for k in self.edge_assets
            if isinstance(self.edge_assets[k], (Concave, Convex))
        ]

    def _get_snapshot(self):
        """Creates a snapshot of the current Infrastructure."""
        snapshot = AssetGraph(
            graph_id="Snapshot",
            node_assets=self.infrastructure.node_assets,
            edge_assets=self.infrastructure.edge_assets,
        )

        for n, attrs in self.infrastructure.nodes(data=True):
            snapshot.add_node(n, strict=False, **attrs)
        for u, v, attrs in self.infrastructure.edges(data=True):
            snapshot.add_edge(u, v, strict=False, **attrs)
        return snapshot

    def _reset(self):
        """Resets the PlacementView to its initial state."""
        self.clear()
        self.residual = self._get_snapshot()
        self.nodes_used_by.clear()

    def _update_view(self, placement: Placement):
        """Creates a view of the infrastructure.

        It adds to the view the resources required by the placement.

        Args:
            placement (Placement): The placement to update the view with.
        """
        if placement.mapping:
            for n, node_reqs in placement.node_requirements_mapping().items():
                new_node_reqs: Dict[str, Any] = self.node_aggregate(
                    self.get_node_view(n), node_reqs
                )
                self.add_node(n, **new_node_reqs)
                self.nodes_used_by[n].add(placement.application.id)
                nx.set_node_attributes(
                    self.residual,
                    {n: self.node_assets.consume(self.residual.nodes[n], node_reqs)},
                )

            for s, t, int_reqs in placement.application.edges(data=True):
                node_s, node_t = (
                    placement.service_placement(s),
                    placement.service_placement(t),
                )
                _path = placement.infrastructure.path(node_s, node_t)
                if _path:
                    path = _path[0]
                    _int_reqs = {
                        k: (
                            self.edge_assets[k].lower_bound
                            if k in self._concave_convex_assets
                            else int_reqs[k]
                        )
                        for k in int_reqs
                    }

                    for n1, n2, _ in path:
                        new_int_reqs = self.edge_aggregate(
                            self.get_edge_view(n1, n2), _int_reqs
                        )

                        self.add_edge(n1, n2, **new_int_reqs)
                        self.nodes_used_by[n1].add(placement.application.id)
                        self.nodes_used_by[n2].add(placement.application.id)
                        nx.set_edge_attributes(
                            self.residual,
                            {
                                (n1, n2): self.edge_assets.consume(
                                    self.residual.edges[n1, n2], new_int_reqs
                                )
                            },
                        )

                    edge_view = self.get_edge_view(node_s, node_t)
                    _int_reqs = {
                        k: (
                            edge_view[k]
                            if k not in self._concave_convex_assets
                            else int_reqs[k]
                        )
                        for k in int_reqs
                        if k in self.edge_assets and self.edge_assets[k].functional
                    }

                    self.add_edge(node_s, node_t, **_int_reqs)
                else:
                    placement.infrastructure.logger.warning(
                        f"Stopping placement search for {placement.application.id}"
                    )
                    placement.infrastructure.logger.warning(
                        f" [Path not found] {s} ({node_s}) -> {t} ({node_t})"
                    )
                    placement._to_reset = True  # pylint: disable=protected-access
                    break
