"""Internet Topology Zoo-backed reference infrastructures.

The Topology Zoo family models published real-world backbone and research
network topologies curated by the Internet Topology Zoo and redistributed
through TopoHub. These references primarily contribute realistic node
placement, inter-site connectivity, and link distances, making them suitable
for WAN latency and geographic-placement studies.

Example:
    .. code-block:: python

        get_topology_zoo("Abilene", **kwargs)

Source:
    Internet Topology Zoo, https://topology-zoo.org/
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ._helpers import get_topohub

if TYPE_CHECKING:
    from collections.abc import Callable

    import networkx as nx

    from eclypse.graph import Infrastructure
    from eclypse.graph.assets import Asset
    from eclypse.placement.strategies import PlacementStrategy
    from eclypse.utils.types import (
        InitPolicy,
        UpdatePolicies,
    )


def get_topology_zoo(
    topology: str,
    infrastructure_id: str | None = None,
    update_policies: UpdatePolicies = None,
    node_assets: dict[str, Asset] | None = None,
    link_assets: dict[str, Asset] | None = None,
    include_default_assets: bool = False,
    resource_init: InitPolicy = "max",
    path_algorithm: Callable[[nx.Graph, str, str], list[str]] | None = None,
    placement_strategy: PlacementStrategy | None = None,
    seed: int | None = None,
) -> Infrastructure:
    """Create a Topology Zoo-backed infrastructure from TopoHub.

    The ``topology`` value must be a valid topology name from
    `TopoHub <https://www.topohub.org>`_'s ``topozoo`` family catalogue.

    Args:
        topology (str):
            Topology Zoo identifier, such as ``"Abilene"``.
        infrastructure_id (str | None):
            Identifier assigned to the infrastructure. If omitted, a dataset-based
            identifier is used.
        update_policies (UpdatePolicies):
            Graph update policies executed during ``evolve()``.
        node_assets (dict[str, Asset] | None):
            Node asset definitions available to the infrastructure.
        link_assets (dict[str, Asset] | None):
            Edge asset definitions available to the infrastructure.
        include_default_assets (bool):
            Whether to include default ECLYPSE assets.
        resource_init (InitPolicy):
            Initialisation policy used for graph assets.
        path_algorithm (Callable[[nx.Graph, str, str], list[str]] | None):
            Path computation function for infrastructure routing.
        placement_strategy (PlacementStrategy | None):
            Optional placement strategy attached to the infrastructure.
        seed (int | None):
            Seed forwarded to the infrastructure random generator.

    Returns:
        Infrastructure: The converted Topology Zoo infrastructure.
    """
    dataset_path = f"topozoo/{topology}"
    return get_topohub(
        topology=dataset_path,
        infrastructure_id=infrastructure_id or f"topology_zoo_{topology.lower()}",
        use_names=True,
        update_policies=update_policies,
        node_assets=node_assets,
        link_assets=link_assets,
        include_default_assets=include_default_assets,
        resource_init=resource_init,
        path_algorithm=path_algorithm,
        placement_strategy=placement_strategy,
        seed=seed,
    )


__all__ = ["get_topology_zoo"]
