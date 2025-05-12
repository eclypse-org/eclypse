# pylint: disable=unnecessary-lambda-assignment,import-outside-toplevel
"""Factory for the SockShop microservice application.

Defines the SockShop e-commerce demo as an Application object, modeling typical user interactions
such as browsing, cart updates, checkout, and order tracking. Each microservice is assigned
realistic compute and performance requirements.

Service interactions and structure are based on:
Sock Shop — A Microservices Demo Application,
https://github.com/ocp-power-demos/sock-shop-demo
"""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Callable,
    Dict,
    List,
    Literal,
    Optional,
    Union,
)

from eclypse_core.utils.tools import prune_assets

from eclypse.graph import Application

if TYPE_CHECKING:
    from networkx.classes.reportviews import (
        EdgeView,
        NodeView,
    )

    from eclypse.graph.assets import Asset


def get_sock_shop(
    application_id: str = "SockShop",
    communication_interface: Optional[Literal["mpi", "rest"]] = None,
    node_update_policy: Optional[Callable[[NodeView], None]] = None,
    edge_update_policy: Optional[Callable[[EdgeView], None]] = None,
    node_assets: Optional[Dict[str, Asset]] = None,
    edge_assets: Optional[Dict[str, Asset]] = None,
    include_default_assets: bool = False,
    requirement_init: Literal["min", "max"] = "min",
    flows: Union[Literal["default"], List[List[str]]] = "default",
    seed: Optional[int] = None,
) -> Application:
    """Get the Sock Shop application.

    Args:
        application_id (str): The ID of the application.
        communication_interface (Optional[Literal["mpi", "rest"]]): The communication interface.
        node_update_policy (Optional[Callable[[NodeView], None]]): A function to update the nodes.
        edge_update_policy (Optional[Callable[[EdgeView], None]]): A function to update the edges.
        node_assets (Optional[Dict[str, Asset]]): The assets of the nodes.
        edge_assets (Optional[Dict[str, Asset]]): The assets of the edges.
        include_default_assets (bool): Whether to include the default assets. Default is False.
        requirement_init (Literal["min", "max"]): The initialization of the requirements.
        flows (Optional[List[List[str]]): The flows of the application.
        seed (Optional[int]): The seed for the random number generator.

    Returns:
        Application: The Sock Shop application.
    """
    if flows == "default":
        _flows = [
            ["FrontendService", "UserService", "FrontendService"],  # Login
            ["FrontendService", "CatalogService", "FrontendService"],  # Browsing
            [
                "FrontendService",
                "CatalogService",
                "CartService",
                "FrontendService",
            ],  # Adding to cart
            [
                "FrontendService",
                "PaymentService",
                "OrderService",
                "ShippingService",
                "FrontendService",
            ],  # Checkout
            [
                "FrontendService",
                "OrderService",
                "ShippingService",
                "FrontendService",
            ],  # Shipping monitoring
        ]
    else:
        _flows = flows

    app = Application(
        application_id=application_id,
        node_update_policy=node_update_policy,
        edge_update_policy=edge_update_policy,
        node_assets=node_assets,
        edge_assets=edge_assets,
        include_default_assets=include_default_assets,
        requirement_init=requirement_init,
        flows=_flows,
        seed=seed,
    )

    if communication_interface is None:
        add_fn = app.add_node
        id_fn = lambda service: service
    elif communication_interface in ["mpi", "rest"]:
        add_fn = app.add_service  # type: ignore[assignment]
        if communication_interface == "mpi":
            from . import mpi_services as services
        else:
            from . import rest_services as services  # type: ignore[no-redef]

        classes = {
            "CatalogService": services.CatalogService,
            "UserService": services.UserService,
            "CartService": services.CartService,
            "OrderService": services.OrderService,
            "PaymentService": services.PaymentService,
            "ShippingService": services.ShippingService,
            "FrontendService": services.FrontendService,
        }
        id_fn = lambda service: classes[service](service)
    else:
        raise ValueError(f"Unknown communication interface: {communication_interface}")

    add_fn(
        id_fn("UserService"),
        **prune_assets(
            app.node_assets,
            cpu=1,
            gpu=0,
            ram=0.75,
            storage=0.3,
            availability=0.91,
            processing_time=10,
        ),
    )
    add_fn(
        id_fn("FrontendService"),
        **prune_assets(
            app.node_assets,
            cpu=1,
            gpu=0,
            ram=0.75,
            storage=0.3,
            availability=0.94,
            processing_time=30,
        ),
    )
    add_fn(
        id_fn("CatalogService"),
        **prune_assets(
            app.node_assets,
            cpu=1,
            gpu=0,
            ram=1.5,
            storage=0.75,
            availability=0.91,
            processing_time=12.5,
        ),
    )
    add_fn(
        id_fn("OrderService"),
        **prune_assets(
            app.node_assets,
            cpu=2,
            gpu=0,
            ram=3.0,
            storage=0.75,
            availability=0.92,
            processing_time=20,
        ),
    )
    add_fn(
        id_fn("CartService"),
        **prune_assets(
            app.node_assets,
            cpu=1,
            gpu=0,
            ram=0.75,
            storage=0.3,
            availability=0.91,
            processing_time=10,
        ),
    )
    add_fn(
        id_fn("PaymentService"),
        **prune_assets(
            app.node_assets,
            cpu=1,
            gpu=0,
            ram=0.75,
            storage=0.3,
            availability=0.95,
            processing_time=12.5,
        ),
    )
    add_fn(
        id_fn("ShippingService"),
        **prune_assets(
            app.node_assets,
            cpu=1,
            gpu=0,
            ram=0.75,
            storage=0.3,
            availability=0.915,
            processing_time=17.5,
        ),
    )

    app.add_edge(
        "FrontendService",
        "CatalogService",
        symmetric=True,
        **prune_assets(app.edge_assets, latency=40, bandwidth=2),
    )
    app.add_edge(
        "FrontendService",
        "UserService",
        symmetric=True,
        **prune_assets(app.edge_assets, latency=40, bandwidth=2),
    )
    app.add_edge(
        "FrontendService",
        "CartService",
        symmetric=True,
        **prune_assets(app.edge_assets, latency=40, bandwidth=2),
    )
    app.add_edge(
        "FrontendService",
        "OrderService",
        symmetric=True,
        **prune_assets(app.edge_assets, latency=50, bandwidth=10),
    )

    app.add_edge(
        "OrderService",
        "PaymentService",
        symmetric=True,
        **prune_assets(latency=50, bandwidth=10),
    )
    app.add_edge(
        "OrderService",
        "ShippingService",
        symmetric=True,
        **prune_assets(app.edge_assets, latency=70, bandwidth=10),
    )

    return app
