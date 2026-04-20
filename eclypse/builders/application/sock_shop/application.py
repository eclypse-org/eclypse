"""Factory for the Sock Shop application."""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Literal,
)

from eclypse.builders.application._helpers import (
    build_application_from_specs,
)

if TYPE_CHECKING:
    from eclypse.graph import Application
    from eclypse.graph.assets import Asset
    from eclypse.utils.types import (
        CommunicationInterface,
        InitPolicy,
        UpdatePolicies,
    )


def get_sock_shop(
    application_id: str = "SockShop",
    communication_interface: CommunicationInterface | None = None,
    update_policies: UpdatePolicies = None,
    node_assets: dict[str, Asset] | None = None,
    edge_assets: dict[str, Asset] | None = None,
    include_default_assets: bool = False,
    requirement_init: InitPolicy = "min",
    flows: Literal["default"] | list[list[str]] = "default",
    store_step: bool = False,
    seed: int | None = None,
) -> Application:
    """Get the Sock Shop application.

    Args:
        application_id (str): The ID of the application.
        communication_interface (CommunicationInterface | None):
            The communication interface.
        update_policies (Callable | list[Callable] | None):
            Graph update policies executed during ``evolve()``.
        node_assets (dict[str, Asset] | None): The assets of the nodes.
        edge_assets (dict[str, Asset] | None): The assets of the edges.
        include_default_assets (bool):
            Whether to include the default assets. Default is False.
        requirement_init (InitPolicy): The initialization of the requirements.
        flows (Literal["default"] | list[list[str]]): The flows of the application.
        store_step (bool):
            Whether instantiated services should store their step outputs in
            the internal step queue. Ignored when
            ``communication_interface`` is ``None``.
        seed (int | None): The seed for the random number generator.

    Returns:
        Application: The Sock Shop application.
    """
    default_flows = [
        ["FrontendService", "UserService", "FrontendService"],
        ["FrontendService", "CatalogService", "FrontendService"],
        [
            "FrontendService",
            "CatalogService",
            "CartService",
            "FrontendService",
        ],
        [
            "FrontendService",
            "PaymentService",
            "OrderService",
            "ShippingService",
            "FrontendService",
        ],
        [
            "FrontendService",
            "OrderService",
            "ShippingService",
            "FrontendService",
        ],
    ]
    service_names = [
        "CatalogService",
        "UserService",
        "CartService",
        "OrderService",
        "PaymentService",
        "ShippingService",
        "FrontendService",
    ]
    node_requirements = {
        "UserService": {
            "cpu": 1,
            "gpu": 0,
            "ram": 0.75,
            "storage": 0.3,
            "availability": 0.91,
            "processing_time": 10,
        },
        "FrontendService": {
            "cpu": 1,
            "gpu": 0,
            "ram": 0.75,
            "storage": 0.3,
            "availability": 0.94,
            "processing_time": 30,
        },
        "CatalogService": {
            "cpu": 1,
            "gpu": 0,
            "ram": 1.5,
            "storage": 0.75,
            "availability": 0.91,
            "processing_time": 12.5,
        },
        "OrderService": {
            "cpu": 2,
            "gpu": 0,
            "ram": 3.0,
            "storage": 0.75,
            "availability": 0.92,
            "processing_time": 20,
        },
        "CartService": {
            "cpu": 1,
            "gpu": 0,
            "ram": 0.75,
            "storage": 0.3,
            "availability": 0.91,
            "processing_time": 10,
        },
        "PaymentService": {
            "cpu": 1,
            "gpu": 0,
            "ram": 0.75,
            "storage": 0.3,
            "availability": 0.95,
            "processing_time": 12.5,
        },
        "ShippingService": {
            "cpu": 1,
            "gpu": 0,
            "ram": 0.75,
            "storage": 0.3,
            "availability": 0.915,
            "processing_time": 17.5,
        },
    }
    edge_requirements = [
        (
            "FrontendService",
            "CatalogService",
            {"symmetric": True, "latency": 40, "bandwidth": 2},
        ),
        (
            "FrontendService",
            "UserService",
            {"symmetric": True, "latency": 40, "bandwidth": 2},
        ),
        (
            "FrontendService",
            "CartService",
            {"symmetric": True, "latency": 40, "bandwidth": 2},
        ),
        (
            "FrontendService",
            "OrderService",
            {"symmetric": True, "latency": 50, "bandwidth": 10},
        ),
        (
            "OrderService",
            "PaymentService",
            {"symmetric": True, "latency": 50, "bandwidth": 10},
        ),
        (
            "OrderService",
            "ShippingService",
            {"symmetric": True, "latency": 70, "bandwidth": 10},
        ),
    ]
    return build_application_from_specs(
        application_id=application_id,
        communication_interface=communication_interface,
        update_policies=update_policies,
        node_assets=node_assets,
        edge_assets=edge_assets,
        include_default_assets=include_default_assets,
        requirement_init=requirement_init,
        flows=flows,
        store_step=store_step,
        default_flows=default_flows,
        service_names=service_names,
        node_requirements=node_requirements,
        edge_requirements=edge_requirements,
        seed=seed,
        package_name=__package__,
    )
