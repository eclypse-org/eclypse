"""Module for the Infrastructure class, which extends the AssetGraph class to represent
a network, with nodes representing devices and edges representing (physical/virtual)
links between them.

The infrastructure also stores:
- A global placement strategy (optional).
- A set of path assets aggregators, one per edge asset.
- A path algorithm to compute the paths between nodes.
- A view of the available nodes and edges.
- A cache of the computed paths and their costs.
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

import networkx as nx
from eclypse_core.graph import Infrastructure as _Infrastructure

from .assets.defaults import (
    get_default_edge_assets,
    get_default_node_assets,
    get_default_path_aggregators,
    group,
    latency,
)

if TYPE_CHECKING:
    from eclypse_core.graph.assets.asset import Asset
    from networkx.classes.reportviews import (
        EdgeView,
        NodeView,
    )

    from eclypse.placement.strategies import PlacementStrategy


class Infrastructure(_Infrastructure):  # pylint: disable=too-few-public-methods
    """Class to represent a Cloud-Edge infrastructure."""

    def __init__(
        self,
        infrastructure_id: str = "Infrastructure",
        placement_strategy: Optional[PlacementStrategy] = None,
        node_update_policy: Optional[Callable[[NodeView], None]] = None,
        edge_update_policy: Optional[Callable[[EdgeView], None]] = None,
        node_assets: Optional[Dict[str, Asset]] = None,
        edge_assets: Optional[Dict[str, Asset]] = None,
        include_default_assets: bool = True,
        path_assets_aggregators: Optional[Dict[str, Callable[[List[Any]], Any]]] = None,
        path_algorithm: Optional[Callable[[nx.Graph, str, str], List[str]]] = None,
        resource_init: Literal["min", "max"] = "min",
        seed: Optional[int] = None,
    ):
        """Create a new Infrastructure.

        Args:
            infrastructure_id (str): The ID of the infrastructure.
            placement_strategy (Optional[PlacementStrategy]): The placement \
                strategy to use.
            node_update_policy (Optional[Callable[[NodeView], None]]): A function to \
                update the nodes.
            edge_update_policy (Optional[Callable[[EdgeView], None]]): A function to \
                update the edges.
            node_assets (Optional[Dict[str, Asset]]): The assets of the nodes.
            edge_assets (Optional[Dict[str, Asset]]): The assets of the edges.
            include_default_assets (bool): Whether to include the default assets.
            path_assets_aggregators (Optional[Dict[str, Callable[[List[Any]], Any]]]): \
                The aggregators to use for the path assets.
            path_algorithm (Optional[Callable[[nx.Graph, str, str], List[str]]]): \
                The algorithm to use to compute the paths.
            resource_init (Literal["min", "max"]): The initialization method for the resources.
            seed (Optional[int]): The seed for the random number generator.
        """

        _node_assets = get_default_node_assets() if include_default_assets else {}
        _edge_assets = get_default_edge_assets() if include_default_assets else {}
        _node_assets.update(node_assets if node_assets is not None else {})
        _edge_assets.update(edge_assets if edge_assets is not None else {})

        _node_assets["group"] = group()  # cannot remove or override NodeGroup
        _edge_assets["latency"] = latency()

        if path_assets_aggregators is not None and not all(
            k in _edge_assets for k in path_assets_aggregators
        ):
            raise ValueError(
                "The path_assets_aggregators must be a subset of the edge_assets"
            )

        default_path_aggregator = get_default_path_aggregators()
        _path_assets_aggregators = (
            path_assets_aggregators if path_assets_aggregators is not None else {}
        )

        for k in _edge_assets:
            if k not in _path_assets_aggregators:
                _path_assets_aggregators[k] = default_path_aggregator[k]

        super().__init__(
            infrastructure_id=infrastructure_id,
            placement_strategy=placement_strategy,
            node_update_policy=node_update_policy,
            edge_update_policy=edge_update_policy,
            node_assets=_node_assets,
            edge_assets=_edge_assets,
            path_assets_aggregators=_path_assets_aggregators,
            path_algorithm=path_algorithm,
            resource_init=resource_init,
            seed=seed,
        )
