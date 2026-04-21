"""Small-world infrastructure generator.

This module provides a Watts-Strogatz style topology generator for infrastructure
graphs with strong local clustering and a small number of long-range shortcuts.
Each node starts in a ring-like neighbourhood, which preserves short-hop local
connectivity, and then a fraction of links is rewired to introduce longer
shortcuts across the graph.

The resulting topology is useful when modelling peer infrastructures with soft
QoS expectations: nearby nodes can communicate through short local paths, while
the added shortcuts reduce the average end-to-end distance for latency-sensitive
traffic without imposing a rigid hierarchy or a single backbone.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import networkx as nx

from eclypse.graph import Infrastructure

if TYPE_CHECKING:
    from collections.abc import Callable

    from eclypse.graph.assets import Asset
    from eclypse.placement.strategies import PlacementStrategy
    from eclypse.utils.types import (
        InitPolicy,
        UpdatePolicies,
    )


def small_world(
    n: int,
    k: int,
    p: float,
    infrastructure_id: str = "small_world",
    symmetric: bool = False,
    update_policies: UpdatePolicies = None,
    node_assets: dict[str, Asset] | None = None,
    link_assets: dict[str, Asset] | None = None,
    include_default_assets: bool = False,
    strict: bool = False,
    resource_init: InitPolicy = "min",
    path_algorithm: Callable[[nx.Graph, str, str], list[str]] | None = None,
    placement_strategy: PlacementStrategy | None = None,
    seed: int | None = None,
) -> Infrastructure:
    """Create a small-world infrastructure using the Watts-Strogatz model.

    Args:
        n (int):
            Number of nodes in the generated topology.
        k (int):
            Number of nearest neighbours joined to each node before rewiring.
        p (float):
            Rewiring probability for each edge in the ring lattice.
        infrastructure_id (str):
            Identifier assigned to the infrastructure.
        symmetric (bool):
            Whether generated links should be mirrored.
        update_policies (UpdatePolicies):
            Graph update policies executed during ``evolve()``.
        node_assets (dict[str, Asset] | None):
            Node asset definitions available to the infrastructure.
        link_assets (dict[str, Asset] | None):
            Edge asset definitions available to the infrastructure.
        include_default_assets (bool):
            Whether to include default ECLYPSE assets.
        strict (bool):
            Whether inconsistent asset values should raise.
        resource_init (InitPolicy):
            Initialisation policy used for graph assets.
        path_algorithm (Callable[[nx.Graph, str, str], list[str]] | None):
            Path computation function for infrastructure routing.
        placement_strategy (PlacementStrategy | None):
            Optional placement strategy attached to the infrastructure.
        seed (int | None):
            Seed forwarded to the random graph model.

    Returns:
        Infrastructure: The generated small-world infrastructure.
    """
    infrastructure = Infrastructure(
        infrastructure_id=infrastructure_id,
        update_policies=update_policies,
        node_assets=node_assets,
        edge_assets=link_assets,
        include_default_assets=include_default_assets,
        resource_init=resource_init,
        path_algorithm=path_algorithm,
        placement_strategy=placement_strategy,
        seed=seed,
    )

    for index in range(n):
        infrastructure.add_node(f"n{index}", strict=strict)

    graph = nx.watts_strogatz_graph(n=n, k=k, p=p, seed=seed)
    node_ids = list(infrastructure.nodes)
    for source, target in graph.edges:
        infrastructure.add_edge(
            node_ids[source],
            node_ids[target],
            symmetric=symmetric,
            strict=strict,
        )

    return infrastructure
