"""Module for the infrastructure builders.
It has the following builders:

- hierarchical: A hierarchical infrastructure made of nodes partitioned into groups.
- star: A star infrastructure with clients connected to a central node.
- random: A random infrastructure with nodes connected with a given probability.
"""

from __future__ import annotations

import math
import random as rnd
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Generator,
    List,
    Literal,
    Optional,
    Tuple,
    Union,
    no_type_check,
)

import networkx as nx
import numpy as np

from eclypse.graph import Infrastructure

if TYPE_CHECKING:
    from eclypse_core.utils.types import ConnectivityFn
    from networkx.classes.reportviews import (
        EdgeView,
        NodeView,
    )

    from eclypse.graph.assets import Asset

DEFAULT_NODE_PARTITIONING = [0.35, 0.3, 0.2, 0.15]


def hierarchical(
    infrastructure_id: str,
    n: int,
    symmetric: bool = False,
    node_partitioning: Optional[List[float]] = None,
    connectivity: Optional[Union[ConnectivityFn, List[float]]] = None,
    cross_level_connectivity: Optional[Union[ConnectivityFn, List[float]]] = None,
    node_update_policy: Optional[Callable[[NodeView], None]] = None,
    link_update_policy: Optional[Callable[[EdgeView], None]] = None,
    node_assets: Optional[Dict[str, Asset]] = None,
    link_assets: Optional[Dict[str, Asset]] = None,
    include_default_assets: bool = False,
    resource_init: Literal["min", "max"] = "max",
    path_algorithm: Optional[Callable[[nx.Graph, str, str], List[str]]] = None,
    seed: Optional[int] = None,
):
    """Create a hierarchical infrastructure made of `n` nodes, with a given partitioning
    of the nodes into `len(node_partitioning)` layers. Nodes of the same level are
    connected with a given probability function or list of probabilities `connectivity`,
    and another function/list of probabilities `cross_level_connectivity` is used to
    connect nodes in the same level.

    Args:

        infrastructure_id (str): The ID of the infrastructure.
        n (int): The number of nodes in the infrastructure.
        symmetric (bool): Whether the connections are symmetric. Defaults to False.
        node_partitioning (Optional[List[float]]]):
            The partitioning of the nodes into groups, specified as a list of
            probabilities. The sum of the probabilities must be 1. Defaults to None.
        connectivity (Optional[Union[ConnectivityFn, List[float]]]): The connectivity \
            function or list of probabilities for the connections between levels. Defaults to None.
        cross_level_connectivity (Optional[Union[ConnectivityFn, List[float]]]):
            The connectivity function or list of probabilities for the connections between nodes\
            in the same level. Defaults to None.
        node_update_policy (Optional[Callable[[NodeView], None]]): The policy to update the nodes.\
            Defaults to None.
        link_update_policy (Optional[Callable[[EdgeView], None]]): The policy to update the links.\
            Defaults to None.
        node_assets (Optional[Dict[str, Asset]]): The assets for the nodes. Defaults to None.
        link_assets (Optional[Dict[str, Asset]]): The assets for the links. Defaults to None.
        include_default_assets (bool): Whether to include the default assets. Defaults to False.
        resource_init (Literal["min", "max"]): The initialization policy for the resources.\
            Defaults to "min".
        path_algorithm (Optional[Callable[[nx.Graph, str, str], List[str]]]): The algorithm to\
            compute the paths between nodes. Defaults to None.
        seed (Optional[int]): The seed for the random number generator. Defaults to None.

    Returns:
        Infrastructure: The hierarchical infrastructure.
    """

    if node_partitioning is None:
        node_partitioning = DEFAULT_NODE_PARTITIONING
    if not math.isclose(sum(node_partitioning), 1.0):
        raise ValueError("The sum of the node distribution must be 1")

    levels = len(node_partitioning)

    connectivity_fn = _get_connectivity_functions(
        connectivity=connectivity,
        length=levels - 1,
        default_prob=1.0,
        seed=seed,
    )

    cross_level_connectivity_fn = _get_connectivity_functions(
        connectivity=cross_level_connectivity,
        length=levels,
        seed=seed,
    )

    nodes = [
        list(section)
        for section in np.array_split(
            np.arange(n), np.cumsum([int(n * p) for p in node_partitioning])[:-1]
        )
    ]
    # rename nodes by group with incremental counter (i.e. l0_1, l0_2, l1_1...)
    nodes = [
        [f"l{i}_{j}" for j in range(len(section))] for i, section in enumerate(nodes)
    ]

    infrastructure = Infrastructure(
        infrastructure_id=infrastructure_id,
        node_update_policy=node_update_policy,
        edge_update_policy=link_update_policy,
        node_assets=node_assets,
        edge_assets=link_assets,
        include_default_assets=include_default_assets,
        resource_init=resource_init,
        path_algorithm=path_algorithm,
        seed=seed,
    )

    for i in range(levels):
        for node in nodes[i]:
            infrastructure.add_node(node)

    for level in range(levels):
        if level < levels - 1:
            for parent, child in connectivity_fn[level](nodes[level], nodes[level + 1]):
                infrastructure.add_edge(parent, child, symmetric=symmetric)
        for n1, n2 in cross_level_connectivity_fn[level](nodes[level], nodes[level]):
            if n1 != n2:
                infrastructure.add_edge(n1, n2, symmetric=symmetric)
    return infrastructure


def star(
    infrastructure_id: str,
    n_clients: int,
    symmetric: bool = False,
    node_update_policy: Optional[Callable[[NodeView], None]] = None,
    link_update_policy: Optional[Callable[[EdgeView], None]] = None,
    node_assets: Optional[Dict[str, Asset]] = None,
    link_assets: Optional[Dict[str, Asset]] = None,
    center_assets_values: Optional[Dict[str, Any]] = None,
    outer_assets_values: Optional[Dict[str, Any]] = None,
    include_default_assets: bool = False,
    resource_init: Literal["min", "max"] = "min",
    path_algorithm: Optional[Callable[[nx.Graph, str, str], List[str]]] = None,
    seed: Optional[int] = None,
):
    """Create a star infrastructure with `n_clients` clients connected to a central
    node. The group of the clients can be specified.

    Args:
        infrastructure_id (str): The ID of the infrastructure.
        n_clients (int): The number of clients in the infrastructure.
        node_update_policy (Optional[Callable[[NodeView], None]]): The policy to update the nodes.\
            Defaults to None.
        link_update_policy (Optional[Callable[[EdgeView], None]]): The policy to update the links.\
            Defaults to None.
        node_assets (Optional[Dict[str, Asset]]): The assets for the nodes. Defaults to None.
        link_assets (Optional[Dict[str, Asset]]): The assets for the links. Defaults to None.
        center_assets_values (Optional[Dict[str, Any]]): The assets for the center node. \
            Defaults to None.
        outer_assets_values (Optional[Dict[str, Any]]): The assets for the outer nodes. \
            Defaults to None.
        include_default_assets (bool): Whether to include the default assets. Defaults to False.
        resource_init (Literal["min", "max"]): The initialization policy for the resources.\
            Defaults to "min".
        path_algorithm (Optional[Callable[[nx.Graph, str, str], List[str]]]): The algorithm to\
            compute the paths between nodes. Defaults to None.
        seed (Optional[int]): The seed for the random number generator. Defaults to None.

    Returns:
        Infrastructure: The star infrastructure.
    """

    infrastructure = Infrastructure(
        infrastructure_id=infrastructure_id,
        node_update_policy=node_update_policy,
        edge_update_policy=link_update_policy,
        node_assets=node_assets,
        edge_assets=link_assets,
        include_default_assets=include_default_assets,
        path_algorithm=path_algorithm,
        resource_init=resource_init,
        seed=seed,
    )
    _outer_assets_values = {} if outer_assets_values is None else outer_assets_values
    _center_assets_values = {} if center_assets_values is None else center_assets_values
    for i in range(n_clients):
        infrastructure.add_node(f"outer_{i}", **_outer_assets_values)
    infrastructure.add_node("center", **_center_assets_values)

    for i in range(n_clients):
        infrastructure.add_edge(f"outer_{i}", "center", symmetric=symmetric)

    return infrastructure


def random(
    infrastructure_id: str,
    n: int,
    p: float = 0.5,
    symmetric: bool = False,
    node_update_policy: Optional[Callable[[NodeView], None]] = None,
    link_update_policy: Optional[Callable[[EdgeView], None]] = None,
    node_assets: Optional[Dict[str, Asset]] = None,
    link_assets: Optional[Dict[str, Asset]] = None,
    include_default_assets: bool = False,
    resource_init: Literal["min", "max"] = "min",
    path_algorithm: Optional[Callable[[nx.Graph, str, str], List[str]]] = None,
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
        resource_init (Literal["min", "max"]): The initialization policy for the resources.\
            Defaults to "min".
        path_algorithm (Optional[Callable[[nx.Graph, str, str], List[str]]]): The algorithm to\
            compute the paths between nodes. Defaults to None.
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
        seed=seed,
    )

    for i in range(n):
        infrastructure.add_node(f"n{i}")

    nodes = list(infrastructure.nodes)
    random_graph = nx.erdos_renyi_graph(n, p, seed=seed)
    for u, v in random_graph.edges:
        infrastructure.add_edge(nodes[u], nodes[v], symmetric=symmetric)

    return infrastructure


def _uniform_level_connectivity(
    l: List[str], l1: List[str], p: float, seed: Optional[int] = None
) -> Generator[Tuple[str, str], None, None]:
    """Generates the connectivity between levels in a hierarchical infrastructure.

    Args:
        n (int): The number of nodes in the higher level.
        m (int): The number of nodes in the lower level.

    Yields:
        Tuple[str, str]: The links between nodes in the higher and lower levels.
    """
    r = rnd.Random(seed)
    connected = [False for _ in l1]
    for parent in l:
        for i, child in enumerate(l1):
            if r.random() < p:
                yield parent, child
                connected[i] = True

    # ensure at least one connection per child
    for i, child in enumerate(l1):
        if not connected[i]:
            yield r.choice(l), child


@no_type_check
def _get_connectivity_functions(
    connectivity: Optional[Union[ConnectivityFn, List[float]]] = None,
    length: int = 0,
    default_prob: float = 0.0,
    seed: Optional[int] = None,
) -> List[ConnectivityFn]:
    """Retrieve the connectivity functions for a hierarchical infrastructure.

    Args:
        connectivity (Optional[Union[ConnectivityFn, List[float]]]): The connectivity function or\
            list of probabilities for the connections between levels.
        length (int): The number of levels in the infrastructure.
        default_prob (float): The default probability for the connections between levels.
        seed (Optional[int]): The seed for the random number generator.

    Returns:
        List[ConnectivityFn]: The list of connectivity functions for the levels.
    """

    if connectivity is None:
        connectivity_fn = [
            lambda l, l1, p=default_prob: _uniform_level_connectivity(
                l, l1, p, seed=seed
            )
        ] * length
    elif isinstance(connectivity, list):
        if len(connectivity) != length:
            raise ValueError(
                "Cross-level connectivity must have a function for each level"
            )

        connectivity_fn = [
            lambda l, l1, p=p: _uniform_level_connectivity(l, l1, p, seed=seed)
            for p in connectivity
        ] * length
    elif callable(connectivity):
        connectivity_fn = [connectivity] * length
    else:
        raise ValueError("Cross-level connectivity must be a function or a list")

    return connectivity_fn
