"""Factory for a hotel reservation microservice application."""

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


def get_hotel_reservation(
    application_id: str = "HotelReservation",
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
    """Get the hotel reservation application.

    Args:
        application_id (str): Identifier assigned to the generated application.
        communication_interface (CommunicationInterface | None):
            Communication backend used to instantiate executable services. When
            ``None``, the builder returns a graph-only application.
        update_policies (Callable | list[Callable] | None):
            Graph update policies executed during ``evolve()``.
        node_assets (dict[str, Asset] | None):
            Optional assets attached to application nodes.
        edge_assets (dict[str, Asset] | None):
            Optional assets attached to application edges.
        include_default_assets (bool):
            Whether default graph assets should be included in the application.
        requirement_init (InitPolicy):
            Initialisation strategy applied to node and edge requirements.
        flows (Literal["default"] | list[list[str]]):
            User-defined application flows. Use ``"default"`` to install the
            benchmark's built-in booking flows.
        store_step (bool):
            Whether instantiated services should store their step outputs in
            the internal step queue. Ignored when
            ``communication_interface`` is ``None``.
        seed (int | None):
            Seed forwarded to the application random generator.

    Returns:
        Application: The configured hotel reservation application.

    Raises:
        ValueError: If ``communication_interface`` is not supported.
    """
    default_flows = [
        ["FrontendService", "SearchService", "FrontendService"],
        ["FrontendService", "ProfileService", "FrontendService"],
        [
            "FrontendService",
            "ReservationService",
            "PaymentService",
            "ReservationService",
            "FrontendService",
        ],
    ]
    service_names = [
        "FrontendService",
        "PaymentService",
        "ProfileService",
        "ReservationService",
        "SearchService",
    ]
    node_requirements = {
        "FrontendService": {
            "cpu": 1,
            "gpu": 0,
            "ram": 0.75,
            "storage": 0.25,
            "availability": 0.96,
            "processing_time": 12,
        },
        "SearchService": {
            "cpu": 2,
            "gpu": 0,
            "ram": 1.5,
            "storage": 0.75,
            "availability": 0.93,
            "processing_time": 14,
        },
        "ProfileService": {
            "cpu": 1,
            "gpu": 0,
            "ram": 1.0,
            "storage": 0.5,
            "availability": 0.95,
            "processing_time": 10,
        },
        "ReservationService": {
            "cpu": 2,
            "gpu": 0,
            "ram": 2.0,
            "storage": 1.0,
            "availability": 0.92,
            "processing_time": 18,
        },
        "PaymentService": {
            "cpu": 1,
            "gpu": 0,
            "ram": 0.75,
            "storage": 0.5,
            "availability": 0.94,
            "processing_time": 12,
        },
    }
    edge_requirements = [
        (
            "FrontendService",
            "SearchService",
            {"symmetric": True, "latency": 35, "bandwidth": 8},
        ),
        (
            "FrontendService",
            "ProfileService",
            {"symmetric": True, "latency": 30, "bandwidth": 5},
        ),
        (
            "FrontendService",
            "ReservationService",
            {"symmetric": True, "latency": 40, "bandwidth": 10},
        ),
        (
            "ReservationService",
            "PaymentService",
            {"symmetric": True, "latency": 25, "bandwidth": 10},
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
