"""BCube infrastructure generator.

This module provides a factory function to instantiate a BCube(k, n) network topology,
a server-centric architecture designed for modular data centers. The topology is
constructed recursively, enabling high fault-tolerance and multiple parallel paths
between servers.

The topology is defined by two parameters:
- `k`: the recursion level (BCube₀, BCube₁, ..., BCube_k)
- `n`: the number of ports per switch (and switches per level)

A BCube(k, n) contains:
- n^(k+1) servers
- k * n^k switches
- Each server is connected to (k + 1) switches, one per level.

The implementation follows the definition from:
Guo et al. "BCube: a high performance, server-centric network architecture for modular data centers"
ACM SIGCOMM Computer Communication Review, 2009. https://dl.acm.org/doi/10.1145/1592568.1592577
"""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Callable,
    Dict,
    List,
    Literal,
    Optional,
)

from eclypse.graph import Infrastructure

if TYPE_CHECKING:
    import networkx as nx
    from networkx.classes.reportviews import (
        EdgeView,
        NodeView,
    )

    from eclypse.graph.assets import Asset
    from eclypse.placement.strategies import PlacementStrategy


def b_cube(
    k: int,
    n: int,
    infrastructure_id: str = "b_cube",
    node_update_policy: Optional[Callable[[NodeView], None]] = None,
    link_update_policy: Optional[Callable[[EdgeView], None]] = None,
    node_assets: Optional[Dict[str, Asset]] = None,
    link_assets: Optional[Dict[str, Asset]] = None,
    include_default_assets: bool = False,
    strict: bool = False,
    resource_init: Literal["min", "max"] = "max",
    path_algorithm: Optional[Callable[[nx.Graph, str, str], List[str]]] = None,
    placement_strategy: Optional[PlacementStrategy] = None,
    seed: Optional[int] = None,
) -> Infrastructure:
    """Factory for generating a BCube(k, n) topology.

    A BCube is a server-centric topology designed for modular data centers.
    It provides multiple parallel paths between servers and is highly fault-tolerant.

    Args:
        k (int): Recursion level of the BCube. Determines depth (e.g., 0 = star).
        n (int): Number of ports per switch, and number of switches per level.
        infrastructure_id (str): Unique ID for the infrastructure instance.\
            Defaults to "b_cube".
        node_update_policy (Optional[Callable[[NodeView], None]]): Policy to update nodes.\
            Defaults to None.
        link_update_policy (Optional[Callable[[EdgeView], None]]): Policy to update links.\
            Defaults to None.
        node_assets (Optional[Dict[str, Asset]]): Optional default attributes for all nodes.\
            Defaults to None.
        link_assets (Optional[Dict[str, Asset]]): Optional default attributes for all links.\
            Defaults to None.
        include_default_assets (bool): Whether to include default assets. \
            Defaults to False.
        strict (bool): If True, raises an error if the asset values are not \
            consistent with their spaces. Defaults to False.
        resource_init (Literal["min", "max"]): Initialization policy for resources. \
            Defaults to "max".
        path_algorithm (Optional[Callable[[nx.Graph, str, str], List[str]]]): \
            Algorithm to compute paths. Defaults to None.
        placement_strategy (Optional[PlacementStrategy]): Strategy for resource placement.\
            Defaults to None.
        seed (Optional[int]): Seed for random number generation. Defaults to None.

    Returns:
        Infrastructure: The BCube topology as an Infrastructure object.
    """
    infra = Infrastructure(
        infrastructure_id=infrastructure_id,
        node_update_policy=node_update_policy,
        edge_update_policy=link_update_policy,
        node_assets=node_assets,
        edge_assets=link_assets,
        include_default_assets=include_default_assets,
        resource_init=resource_init,
        path_algorithm=path_algorithm,
        placement_strategy=placement_strategy,
        seed=seed,
    )

    # Total number of servers
    num_servers = n ** (k + 1)
    servers = [f"server_{i}" for i in range(num_servers)]
    for s in servers:
        infra.add_node(s, strict=strict)

    # Add switches and connect them to servers
    for level in range(k + 1):
        num_switches = n**level
        for sw_idx in range(num_switches):
            sw_id = f"sw_{level}_{sw_idx}"
            infra.add_node(sw_id, strict=strict)
            for port in range(n):
                server_idx = (
                    sw_idx * n + port if level == 0 else port * n**level + sw_idx
                )
                server_id = f"server_{server_idx}"
                infra.add_edge(sw_id, server_id, symmetric=True)

    return infra
