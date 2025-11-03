"""Module for the Application class.

It extends the AssetGraph class to represent an application, with nodes representing
services and edges representing the interactions between them.
"""

from __future__ import annotations

from functools import cached_property
from typing import (
    TYPE_CHECKING,
    Callable,
    Dict,
    List,
    Literal,
    Optional,
    Union,
)

import networkx as nx

from eclypse.graph import AssetGraph
from eclypse.graph.assets.defaults import (
    get_default_edge_assets,
    get_default_node_assets,
)
from eclypse.remote.service import Service

if TYPE_CHECKING:
    from networkx.classes.reportviews import (
        EdgeView,
        NodeView,
    )

    from .assets import Asset


class Application(AssetGraph):  # pylint: disable=too-few-public-methods
    """Class to represent a multi-service Application."""

    def __init__(
        self,
        application_id: str,
        node_update_policy: Optional[
            Union[Callable[[NodeView], None], List[Callable[[NodeView], None]]]
        ] = None,
        edge_update_policy: Optional[
            Union[Callable[[EdgeView], None], List[Callable[[EdgeView], None]]]
        ] = None,
        node_assets: Optional[Dict[str, Asset]] = None,
        edge_assets: Optional[Dict[str, Asset]] = None,
        include_default_assets: bool = False,
        requirement_init: Literal["min", "max"] = "min",
        flows: Optional[List[List[str]]] = None,
        seed: Optional[int] = None,
    ):
        """Create a new Application.

        Args:
            application_id (str): The ID of the application.
            node_update_policy (Optional[Union[Callable, List[Callable]]]):\
                A function to update the nodes. Defaults to None.
            edge_update_policy (Optional[Union[Callable, List[Callable]]]):\
                A function to update the edges. Defaults to None.
            node_assets (Optional[Dict[str, Asset]]): The assets of the nodes.
            edge_assets (Optional[Dict[str, Asset]]): The assets of the edges.
            include_default_assets (bool): Whether to include the default assets. \
                Defaults to False.
            requirement_init (Literal["min", "max"]): The initialization of the requirements.
            flows (Optional[List[List[str]]): The flows of the application.
            seed (Optional[int]): The seed for the random number generator.
        """
        _node_assets = get_default_node_assets() if include_default_assets else {}
        _edge_assets = get_default_edge_assets() if include_default_assets else {}
        _node_assets.update(node_assets if node_assets is not None else {})
        _edge_assets.update(edge_assets if edge_assets is not None else {})

        super().__init__(
            graph_id=application_id,
            node_update_policy=node_update_policy,
            edge_update_policy=edge_update_policy,
            node_assets=_node_assets,
            edge_assets=_edge_assets,
            attr_init=requirement_init,
            seed=seed,
            flip_assets=True,
        )

        self.services: Dict[str, Service] = {}
        self.flows = flows if flows is not None else []

    def add_service(self, service: Service, **assets):
        """Add a service to the application.

        Args:
            service (Service): The service to add.
            **assets : The assets to add to the service.
        """
        if not isinstance(service, Service):
            raise ValueError("The service must be an instance of Service.")
        service.application_id = self.id
        self.services[service.id] = service
        self.add_node(service.id, **assets)

    def set_flows(self):
        """Set the flows of the application, using the following rules.

        - If the flows are already set, do nothing.
        - If the flows are not set, use the gateway as the source and all\
            the other nodes as the target.
        - If there is no gateway, set the flows to an empty list.
        """
        if self.flows == []:
            gateway_name = next((s for s in self.nodes if "gateway" in s.lower()), None)
            if gateway_name is not None:
                self.flows = list(
                    nx.all_simple_paths(
                        self,
                        source=gateway_name,
                        target=[x for x in self.nodes if x != gateway_name],
                    )
                )

    @cached_property
    def has_logic(self) -> bool:
        """Check if the application has a logic for each service.

        This property requires to be True for the remote execution.
        """
        checks = [(x in self.services) for x in self.nodes]
        return checks != [] and all(checks)
