"""Module for the Placement class.

It represents the mapping of application services onto infrastructure nodes, a
ccording to a placement strategy.
"""

from __future__ import annotations

from collections import defaultdict
from typing import (
    TYPE_CHECKING,
    Any,
)

if TYPE_CHECKING:
    from eclypse.graph.application import Application
    from eclypse.graph.infrastructure import Infrastructure
    from eclypse.placement.view import PlacementView

    from .strategies.strategy import PlacementStrategy


class Placement:
    """Placement class.

    A placement is a mapping of each service of an application to a node of an
    infrastructure, computed according to a placement strategy.
    """

    def __init__(
        self,
        infrastructure: Infrastructure,
        application: Application,
        strategy: PlacementStrategy | None = None,
    ):
        """Initializes the Placement.

        Args:
            infrastructure (Infrastructure):
                The infrastructure to place the application onto.
            application (Application):
                The application to place onto the infrastructure.
            strategy (PlacementStrategy): The strategy to use for the placement.
        """
        self.strategy: PlacementStrategy | None = strategy

        self.infrastructure: Infrastructure = infrastructure
        self.application: Application = application

        self._deployed: bool = False
        self.mapping: dict[str, str] = {}

        self._to_reset = False

    def _generate_mapping(
        self, placements: dict[str, Placement], placement_view: PlacementView
    ):
        """Generate the mapping {service: node}, according to the placement strategy."""
        if self.strategy is None:
            raise ValueError("No placement strategy provided")
        self.mapping = self.strategy.place(
            self.infrastructure.available, self.application, placements, placement_view
        )

    def _reset_mapping(self):
        """Reset the mapping of the placement."""
        self.mapping = {}
        self.clear_reset()

    def mark_for_reset(self):
        """Mark the placement so it will be reset during enactment."""
        self._to_reset = True

    def clear_reset(self):
        """Clear the pending reset marker."""
        self._to_reset = False

    def mark_deployed(self):
        """Mark the placement as deployed on the remote infrastructure."""
        self._deployed = True

    def mark_undeployed(self):
        """Mark the placement as no longer deployed."""
        self._deployed = False

    def service_placement(self, service_id: str) -> str:
        """Return the node where a service is placed.

        Args:
            service_id (str): The name of the service.

        Returns:
            str: The name of the node where the service is placed.
        """
        return self.mapping[service_id]

    def services_on_node(self, node_name: str) -> list[str]:
        """Return all the services placed on a node.

        Args:
            node_name (str): The name of the node.

        Returns:
            list[str]: The names of the services placed on the node.
        """
        return [
            service_id for service_id, node in self.mapping.items() if node == node_name
        ]

    def interactions_on_link(self, source: str, target: str) -> list[tuple[str, str]]:
        """Return all the services interactions crossing a link.

        Args:
            source (str): The name of the source node.
            target (str): The name of the target node.

        Returns:
            list[tuple[str, str]]:
                The names of the services interactions crossing the link.
        """
        services_by_node = self.node_service_mapping()
        path_cache: dict[
            tuple[str, str], list[tuple[str, str, dict[str, Any]]] | None
        ] = {}
        return self._incoming_interactions_on_link(
            source, target, services_by_node, path_cache
        ) + self._outgoing_interactions_on_link(
            source, target, services_by_node, path_cache
        )

    def _get_cached_path(
        self,
        path_cache: dict[tuple[str, str], list[tuple[str, str, dict[str, Any]]] | None],
        source: str,
        target: str,
    ) -> list[tuple[str, str, dict[str, Any]]] | None:
        """Return a cached infrastructure path between two nodes."""
        key = (source, target)
        if key not in path_cache:
            path_cache[key] = self.infrastructure.path(source, target)
        return path_cache[key]

    @staticmethod
    def _path_crosses_link(
        path: list[tuple[str, str, dict[str, Any]]] | None,
        source: str,
        target: str,
    ) -> bool:
        """Check whether a path traverses the given infrastructure link."""
        if path is None:
            return False
        return any(u == source and v == target for u, v, _ in path)

    def _incoming_interactions_on_link(
        self,
        source: str,
        target: str,
        services_by_node: dict[str, list[str]],
        path_cache: dict[tuple[str, str], list[tuple[str, str, dict[str, Any]]] | None],
    ) -> list[tuple[str, str]]:
        """Collect interactions whose callee is placed on the target node."""
        interactions = []
        for callee in services_by_node[target]:
            for caller in self.application.neighbors(callee):
                caller_node = self.service_placement(caller)
                if caller_node == target:
                    continue
                path = self._get_cached_path(path_cache, caller_node, target)
                if self._path_crosses_link(path, source, target):
                    interactions.append((caller, callee))
        return interactions

    def _outgoing_interactions_on_link(
        self,
        source: str,
        target: str,
        services_by_node: dict[str, list[str]],
        path_cache: dict[tuple[str, str], list[tuple[str, str, dict[str, Any]]] | None],
    ) -> list[tuple[str, str]]:
        """Collect interactions whose caller is placed on the source node."""
        interactions = []
        for caller in services_by_node[source]:
            for callee in self.application.neighbors(caller):
                callee_node = self.service_placement(callee)
                if callee_node == source:
                    continue
                path = self._get_cached_path(path_cache, source, callee_node)
                if self._path_crosses_link(path, source, target):
                    interactions.append((caller, callee))
        return interactions

    def node_service_mapping(self) -> dict[str, list[str]]:
        """Return a view of the placement.

        Returns:
            dict[str, list[str]]:
                The mapping of nodes to the list of services placed on
                them.
        """
        node_services: defaultdict[str, list[str]] = defaultdict(list)
        for node in self.infrastructure.nodes:
            node_services[node]
        for service_id, node in self.mapping.items():
            node_services[node].append(service_id)
        return dict(node_services)

    def link_interaction_mapping(self) -> dict[tuple[str, str], list[tuple[str, str]]]:
        """Return a view of the placement.

        Returns:
            dict[tuple[str, str], list[tuple[str, str]]]:
                The mapping of links to the list of services
                interactions crossing them.
        """
        return {
            (source, target): self.interactions_on_link(source, target)
            for source, target in self.infrastructure.edges
        }

    def node_requirements_mapping(self) -> dict[str, dict[str, Any]]:
        """Return a view of the placement.

        Returns:
            dict[str, ServiceRequirements]:
                The mapping of nodes to the total requirements of the
                services placed on them.
        """
        return {
            node: self.application.node_assets.aggregate(
                *(
                    self.application.nodes[s]
                    for s in services
                    if self.application.has_node(s)  # check if service exists
                )
            )
            for node, services in self.node_service_mapping().items()
        }

    def link_requirements_mapping(self) -> dict[tuple[str, str], dict[str, Any]]:
        """Return a view of the placement.

        Returns:
            dict[tuple[str, str], S2SRequirements]: The mapping of links to the total
                requirements of the services interactions crossing them.
        """
        return {
            (source, target): self.application.edge_assets.aggregate(
                *(
                    self.application.edges[s, t]
                    for s, t in services
                    if self.application.has_edge(s, t)  # check if interaction exists
                )
            )
            for (source, target), services in self.link_interaction_mapping().items()
        }

    def __str__(self) -> str:
        """Return a string representation of the placement.

        Returns:
            str: The string representation of the placement, in the form:
                <service_id> -> <node_name>
        """
        result = (
            "{"
            + "".join(
                [
                    f"{service_id} -> {node_name} | "
                    for service_id, node_name in self.mapping.items()
                ]
            )[:-3]
            + "}"
        )
        return result

    def __repr__(self) -> str:
        """Return a string representation of the placement.

        Returns:
            str: The string representation of the placement, in the form:
            <service_id> -> <node_name>
        """
        return self.__str__()

    @property
    def is_partial(self) -> list[str]:
        """Return whether the placement is partial or not.

        Returns:
            list[str]: The list of services that are not placed.
        """
        return list(
            service
            for service in self.application.nodes
            if service not in self.mapping or self.mapping[service] is None
        )

    @property
    def reset_requested(self) -> bool:
        """Return whether the placement is marked for reset."""
        return self._to_reset

    @property
    def deployed(self) -> bool:
        """Return whether the placement has been remotely deployed."""
        return self._deployed
