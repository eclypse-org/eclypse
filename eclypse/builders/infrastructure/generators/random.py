"""Random infrastructure generator.

This module provides a generator for creating unstructured network topologies using
the Erdos-Rényi random graph model. Each pair of nodes has a configurable probability
`p` of being connected, allowing the simulation of a wide variety of sparse or dense graphs.

This is useful for stress-testing placement or routing algorithms, comparing performance
against structured topologies, or modeling loosely connected networks such as P2P overlays
or ad-hoc wireless systems.
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


def random(
    n: int,
    infrastructure_id: str = "random",
    p: float = 0.5,
    symmetric: bool = False,
    node_update_policy: Optional[Callable[[NodeView], None]] = None,
    link_update_policy: Optional[Callable[[EdgeView], None]] = None,
    node_assets: Optional[Dict[str, Asset]] = None,
    link_assets: Optional[Dict[str, Asset]] = None,
    include_default_assets: bool = False,
    strict: bool = False,
    resource_init: Literal["min", "max"] = "min",
    path_algorithm: Optional[Callable[[nx.Graph, str, str], List[str]]] = None,
    placement_strategy: Optional[PlacementStrategy] = None,
    seed: Optional[int] = None,
):
    """Create a random infrastructure with `n` nodes and a given probability `p` of
    connecting two nodes. The nodes are partitioned into groups according to the
    provided distribution.

    Args:
        infrastructure_id (str): The ID of the infrastructure.
        n (int): The number of nodes in the infrastructure.
        p (float): The probability of connecting two nodes. Defaults to 0.5.
        node_update_policy (Optional[Callable[[NodeView], None]]): The policy to update the nodes.\
            Defaults to None.
        link_update_policy (Optional[Callable[[EdgeView], None]]): The policy to update the links.\
            Defaults to None.
        node_assets (Optional[Dict[str, Asset]]): The assets for the nodes. Defaults to None.
        link_assets (Optional[Dict[str, Asset]]): The assets for the links. Defaults to None.
        include_default_assets (bool): Whether to include the default assets. Defaults to False.
        strict (bool): If True, raises an error if the asset values are not \
            consistent with their spaces. Defaults to False.
        resource_init (Literal["min", "max"]): The initialization policy for the resources.\
            Defaults to "min".
        path_algorithm (Optional[Callable[[nx.Graph, str, str], List[str]]]): The algorithm to\
            compute the paths between nodes. Defaults to None.
        placement_strategy (Optional[PlacementStrategy]): The strategy to place the resources.\
            Defaults to None.
        seed (Optional[int]): The seed for the random number generator. Defaults to None.

    Returns:
        Infrastructure: The random infrastructure.
    """

    infrastructure = Infrastructure(
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

    for i in range(n):
        infrastructure.add_node(f"n{i}", strict=strict)

    nodes = list(infrastructure.nodes)
    random_graph = nx.erdos_renyi_graph(n, p, seed=seed)
    for u, v in random_graph.edges:
        infrastructure.add_edge(nodes[u], nodes[v], symmetric=symmetric, strict=strict)

    return infrastructure
