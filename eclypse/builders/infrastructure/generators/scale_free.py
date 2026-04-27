"""Scale-free infrastructure generator.

This module provides a Barabasi-Albert style topology generator for infrastructure
graphs dominated by a small number of highly connected hubs. New nodes attach
preferentially to already well-connected nodes, creating a network with a few
backbone-like hubs and many low-degree peripheral nodes.

This is useful for infrastructures where QoS depends on hub capacity and
resilience: most flows traverse a limited set of critical nodes, so the topology
is well suited to studying congestion, bottlenecks, and the impact of hub
failures on latency and bandwidth.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

import networkx as nx

from eclypse.graph import Infrastructure

if TYPE_CHECKING:
    from collections.abc import Callable

    from eclypse.graph.assets import Asset
    from eclypse.utils.types import (
        InitPolicy,
        UpdatePolicies,
    )


def get_scale_free(
    n: int,
    m: int,
    infrastructure_id: str = "scale_free",
    symmetric: bool = False,
    update_policies: UpdatePolicies = None,
    node_assets: dict[str, Asset] | None = None,
    link_assets: dict[str, Asset] | None = None,
    include_default_assets: bool = False,
    strict: bool = False,
    resource_init: InitPolicy = "min",
    path_algorithm: Callable[[nx.Graph, str, str], list[str]] | None = None,
    seed: int | None = None,
) -> Infrastructure:
    """Create a scale-free infrastructure using the Barabasi-Albert model.

    Args:
        n (int):
            Number of nodes in the generated topology.
        m (int):
            Number of edges attached from each new node to existing nodes.
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
        seed (int | None):
            Seed forwarded to the random graph model.

    Returns:
        Infrastructure: The generated scale-free infrastructure.
    """
    infrastructure = Infrastructure(
        infrastructure_id=infrastructure_id,
        update_policies=update_policies,
        node_assets=node_assets,
        edge_assets=link_assets,
        include_default_assets=include_default_assets,
        resource_init=resource_init,
        path_algorithm=path_algorithm,
        seed=seed,
    )

    for index in range(n):
        infrastructure.add_node(f"n{index}", strict=strict)

    graph = nx.barabasi_albert_graph(n=n, m=m, seed=seed)
    node_ids = list(infrastructure.nodes)
    for source, target in graph.edges:
        infrastructure.add_edge(
            node_ids[source],
            node_ids[target],
            symmetric=symmetric,
            strict=strict,
        )

    return infrastructure
