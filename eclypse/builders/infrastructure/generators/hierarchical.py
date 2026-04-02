"""Hierarchical infrastructure generator.

This module provides a generator function for creating hierarchical network topologies.
Nodes are partitioned into multiple layers according to a specified distribution, and
connections are established both within and across layers based on custom or uniform
probability models.

Such topologies are useful for modeling structured systems with layered organization,
like sensor networks, enterprise infrastructures, or cloud-fog-edge computing stacks.
"""

from __future__ import annotations

import math
import random as rnd
from typing import (
    TYPE_CHECKING,
    Literal,
    no_type_check,
)

import numpy as np

from eclypse.graph import Infrastructure

if TYPE_CHECKING:
    from collections.abc import (
        Callable,
        Generator,
    )

    from networkx import nx
    from networkx.classes.reportviews import (
        EdgeView,
        NodeView,
    )

    from eclypse.graph.assets import Asset
    from eclypse.placement.strategies import PlacementStrategy
    from eclypse.utils.types import ConnectivityFn

DEFAULT_NODE_PARTITIONING = [0.35, 0.3, 0.2, 0.15]


def hierarchical(
    n: int,
    infrastructure_id: str = "hierarchical",
    symmetric: bool = False,
    node_partitioning: list[float] | None = None,
    connectivity: ConnectivityFn | list[float] | None = None,
    cross_level_connectivity: ConnectivityFn | list[float] | None = None,
    node_update_policy: Callable[[NodeView], None] | None = None,
    link_update_policy: Callable[[EdgeView], None] | None = None,
    node_assets: dict[str, Asset] | None = None,
    link_assets: dict[str, Asset] | None = None,
    include_default_assets: bool = False,
    strict: bool = False,
    resource_init: Literal["min", "max"] = "max",
    placement_strategy: PlacementStrategy | None = None,
    path_algorithm: Callable[[nx.Graph, str, str], list[str]] | None = None,
    seed: int | None = None,
):
    """Create a hierarchical infrastructure made of `n` nodes.

    It uses the given partitioning of the nodes into `len(node_partitioning)` layers.
    Nodes of the same level are connected with a given probability function or list of
    probabilities `connectivity`, and another function/list of probabilities
    `cross_level_connectivity` is used to connect nodes in the same level.

    Args:
        infrastructure_id (str): The ID of the infrastructure.
        n (int): The number of nodes in the infrastructure.
        symmetric (bool): Whether the connections are symmetric. Defaults to False.
        node_partitioning (list[float] | None]):
            The partitioning of the nodes into groups, specified as a list of
            probabilities. The sum of the probabilities must be 1. Defaults to None.
        connectivity (ConnectivityFn | list[float] | None): The connectivity \
            function or list of probabilities for the connections between levels. Defaults to None.
        cross_level_connectivity (ConnectivityFn | list[float] | None):
            The connectivity function or list of probabilities for the connections between nodes\
            in the same level. Defaults to None.
        node_update_policy (Callable[[NodeView], None] | None): The policy to update the nodes.\
            Defaults to None.
        link_update_policy (Callable[[EdgeView], None] | None): The policy to update the links.\
            Defaults to None.
        node_assets (dict[str, Asset] | None): The assets for the nodes. Defaults to None.
        link_assets (dict[str, Asset] | None): The assets for the links. Defaults to None.
        include_default_assets (bool): Whether to include the default assets. Defaults to False.
        strict (bool): If True, raises an error if the asset values are not \
            consistent with their spaces. Defaults to False.
        resource_init (Literal["min", "max"]): The initialization policy for the resources.\
            Defaults to "min".
        placement_strategy (PlacementStrategy | None): The placement strategy for the\
            infrastructure. Defaults to None.
        path_algorithm (Callable[[nx.Graph, str, str], list[str]] | None): The algorithm to\
            compute the paths between nodes. Defaults to None.
        seed (int | None): The seed for the random number generator. Defaults to None.

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
        placement_strategy=placement_strategy,
        seed=seed,
    )

    for i in range(levels):
        for node in nodes[i]:
            infrastructure.add_node(node, strict=strict)

    for level in range(levels):
        if level < levels - 1:
            for parent, child in connectivity_fn[level](nodes[level], nodes[level + 1]):
                infrastructure.add_edge(
                    parent, child, symmetric=symmetric, strict=strict
                )
        for n1, n2 in cross_level_connectivity_fn[level](nodes[level], nodes[level]):
            if n1 != n2:
                infrastructure.add_edge(n1, n2, symmetric=symmetric, strict=strict)
    return infrastructure


@no_type_check
def _get_connectivity_functions(
    connectivity: ConnectivityFn | list[float] | None = None,
    length: int = 0,
    default_prob: float = 0.0,
    seed: int | None = None,
) -> list[ConnectivityFn]:
    """Retrieve the connectivity functions for a hierarchical infrastructure.

    Args:
        connectivity (ConnectivityFn | list[float] | None): The connectivity function or\
            list of probabilities for the connections between levels.
        length (int): The number of levels in the infrastructure.
        default_prob (float): The default probability for the connections between levels.
        seed (int | None): The seed for the random number generator.

    Returns:
        list[ConnectivityFn]: The list of connectivity functions for the levels.
    """
    if connectivity is None:
        connectivity_fn = [
            lambda layer, layer1, p=default_prob: _uniform_level_connectivity(
                layer, layer1, p, seed=seed
            )
        ] * length
    elif isinstance(connectivity, list):
        if len(connectivity) != length:
            raise ValueError(
                "Cross-level connectivity must have a function for each level"
            )

        connectivity_fn = [
            lambda layer, layer1, p=p: _uniform_level_connectivity(
                layer, layer1, p, seed=seed
            )
            for p in connectivity
        ] * length
    elif callable(connectivity):
        connectivity_fn = [connectivity] * length
    else:
        raise ValueError("Cross-level connectivity must be a function or a list")

    return connectivity_fn


def _uniform_level_connectivity(
    layer: list[str], layer1: list[str], p: float, seed: int | None = None
) -> Generator[tuple[str, str], None, None]:
    """Generates the connectivity between levels in a hierarchical infrastructure.

    Args:
        layer (list[str]): The nodes in the higher level.
        layer1 (list[str]): The nodes in the lower level.
        p (float): The probability of connecting two nodes.
        seed (int | None): The seed for the random number generator.

    Yields:
        tuple[str, str]: The links between nodes in the higher and lower levels.
    """
    r = rnd.Random(seed)
    connected = [False for _ in layer1]
    for parent in layer:
        for i, child in enumerate(layer1):
            if r.random() < p:
                yield parent, child
                connected[i] = True

                # ensure at least one connection per child
    for i, child in enumerate(layer1):
        if not connected[i]:
            yield r.choice(layer), child
