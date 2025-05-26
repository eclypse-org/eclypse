"""Star infrastructure generator.

This module provides a generator for building star-shaped network topologies, where a
central node is connected directly to multiple peripheral client nodes. The center can
be configured separately from the outer nodes in terms of resource assets and roles.

This topology is useful for modeling centralized communication systems such as access
points, base stations, master-slave control, or cloud-edge scenarios with a hub-spoke
structure.
"""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
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


def star(
    n_clients: int,
    infrastructure_id: str = "star",
    symmetric: bool = False,
    node_update_policy: Optional[Callable[[NodeView], None]] = None,
    link_update_policy: Optional[Callable[[EdgeView], None]] = None,
    node_assets: Optional[Dict[str, Asset]] = None,
    link_assets: Optional[Dict[str, Asset]] = None,
    center_assets_values: Optional[Dict[str, Any]] = None,
    outer_assets_values: Optional[Dict[str, Any]] = None,
    include_default_assets: bool = False,
    strict: bool = False,
    resource_init: Literal["min", "max"] = "min",
    path_algorithm: Optional[Callable[[nx.Graph, str, str], List[str]]] = None,
    placement_strategy: Optional[PlacementStrategy] = None,
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
        strict (bool): If True, raises an error if the asset values are not \
            consistent with their spaces. Defaults to False.
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
        resource_init=resource_init,
        path_algorithm=path_algorithm,
        placement_strategy=placement_strategy,
        seed=seed,
    )
    _outer_assets_values = {} if outer_assets_values is None else outer_assets_values
    _center_assets_values = {} if center_assets_values is None else center_assets_values
    for i in range(n_clients):
        infrastructure.add_node(f"outer_{i}", strict=strict, **_outer_assets_values)
    infrastructure.add_node("center", strict=strict, **_center_assets_values)

    for i in range(n_clients):
        infrastructure.add_edge(
            f"outer_{i}", "center", symmetric=symmetric, strict=strict
        )

    return infrastructure
