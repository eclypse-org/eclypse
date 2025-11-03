"""Fat-Tree infrastructure generator.

This module provides a factory function to instantiate a Fat-Tree network topology
commonly used in data center environments. The topology includes core, aggregation,
and edge switches, as well as hosts connected to edge switches.

The size and structure of the topology are determined by the `k` parameter, which must
be an even number. The number of pods is equal to `k`, and the total number of hosts
is `k^3 / 4`.

The implementation follows the definition from:
Mohammad Al-Fares et al. "A Scalable, Commodity Data Center Network Architecture."
ACM SIGCOMM CCR, 2008, https://dl.acm.org/doi/10.1145/1402958.1402967
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


def fat_tree(
    k: int,
    infrastructure_id: str = "fat_tree",
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
    """Factory for generating a Fat-Tree network topology.

    This function builds a symmetrical Fat-Tree structure with parameter `k`,
    used to simulate scalable data center topologies. The resulting Infrastructure
    includes core, aggregation, and edge switches, as well as connected hosts.

    Args:
        k (int): The Fat-Tree parameter, must be an even number. Determines the size and \
            structure of the Fat-Tree topology.
        infrastructure_id (str): Unique ID for the infrastructure instance.\
            Defaults to "fat_tree".
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
        Infrastructure: A Fat-Tree topology with switches and hosts.
    """
    if k % 2 != 0:
        raise ValueError(f"k must be an even number (got {k}) for a Fat-Tree topology.")

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
    num_pods = k
    num_core_switches = (num_pods // 2) ** 2
    num_agg_switches_per_pod = num_pods // 2
    num_edge_switches_per_pod = num_pods // 2
    num_hosts_per_edge = num_pods // 2

    # Core switches
    for i in range(num_core_switches):
        core_id = f"core_{i}"
        infra.add_node(core_id, strict=strict)

    # Pods
    for pod in range(num_pods):
        # Aggregation switches
        agg_switches = []
        for a in range(num_agg_switches_per_pod):
            agg_id = f"agg_{pod}_{a}"
            agg_switches.append(agg_id)
            infra.add_node(agg_id, strict=strict)

        # Edge switches + hosts
        for e in range(num_edge_switches_per_pod):
            edge_id = f"edge_{pod}_{e}"
            infra.add_node(edge_id, strict=strict)
            # Edge <-> Aggregation
            for agg_id in agg_switches:
                infra.add_edge(edge_id, agg_id, symmetric=True, strict=strict)

            # Hosts under edge
            for h in range(num_hosts_per_edge):
                host_id = f"host_{pod}_{e}_{h}"
                infra.add_node(host_id, strict=strict)
                infra.add_edge(host_id, edge_id, symmetric=True, strict=strict)

        # Aggregation <-> Core
        for i, agg_id in enumerate(agg_switches):
            for j in range(num_pods // 2):
                core_index = i * (num_pods // 2) + j
                core_id = f"core_{core_index}"
                infra.add_edge(agg_id, core_id, symmetric=True, strict=strict)

    return infra
