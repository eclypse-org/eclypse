"""Module for the Application class.

It extends the AssetGraph class to represent an application, with nodes representing
services and edges representing the interactions between them.
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

from eclypse_core.graph import Application as _Application

from .assets.defaults import (
    get_default_edge_assets,
    get_default_node_assets,
    group,
    latency,
)

if TYPE_CHECKING:
    from networkx.classes.reportviews import (
        EdgeView,
        NodeView,
    )

    from .assets import Asset


class Application(_Application):  # pylint: disable=too-few-public-methods
    """Class to represent a multi-service Application."""

    def __init__(
        self,
        application_id: str,
        node_update_policy: Optional[Callable[[NodeView], None]] = None,
        edge_update_policy: Optional[Callable[[EdgeView], None]] = None,
        node_assets: Optional[Dict[str, Asset]] = None,
        edge_assets: Optional[Dict[str, Asset]] = None,
        include_default_assets: bool = True,
        requirement_init: Literal["min", "max"] = "min",
        flows: Optional[List[List[str]]] = None,
        seed: Optional[int] = None,
    ):
        """Create a new Application.

        Args:
            application_id (str): The ID of the application.
            node_update_policy (Optional[Callable[[NodeView], None]]): A function to \
                update the nodes.
            edge_update_policy (Optional[Callable[[EdgeView], None]]): A function to \
                update the edges.
            node_assets (Optional[Dict[str, Asset]]): The assets of the nodes.
            edge_assets (Optional[Dict[str, Asset]]): The assets of the edges.
            include_default_assets (bool): Whether to include the default assets.
            requirement_init (Literal["min", "max"]): The initialization of the requirements.
            flows (Optional[List[List[str]]): The flows of the application.
            seed (Optional[int]): The seed for the random number generator.
        """

        _node_assets = get_default_node_assets() if include_default_assets else {}
        _edge_assets = get_default_edge_assets() if include_default_assets else {}
        _node_assets.update(node_assets if node_assets is not None else {})
        _edge_assets.update(edge_assets if edge_assets is not None else {})

        _node_assets["group"] = group()  # cannot remove or override NodeGroup
        _edge_assets["latency"] = latency()

        super().__init__(
            application_id=application_id,
            node_update_policy=node_update_policy,
            edge_update_policy=edge_update_policy,
            node_assets=_node_assets,
            edge_assets=_edge_assets,
            requirement_init=requirement_init,
            flows=flows,
            seed=seed,
        )
