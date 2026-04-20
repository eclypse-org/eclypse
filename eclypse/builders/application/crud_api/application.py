"""Factory for a CRUD API application."""

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


def get_crud_api(
    application_id: str = "CRUDAPI",
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
    """Get the CRUD API application.

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
            benchmark's built-in CRUD request paths.
        store_step (bool):
            Whether instantiated services should store their step outputs in
            the internal step queue. Ignored when
            ``communication_interface`` is ``None``.
        seed (int | None):
            Seed forwarded to the application random generator.

    Returns:
        Application: The configured CRUD API application.

    Raises:
        ValueError: If ``communication_interface`` is not supported.
    """
    default_flows = [
        ["GatewayService", "AuthService", "GatewayService"],
        ["GatewayService", "ItemService", "AuditService", "GatewayService"],
    ]
    service_names = [
        "AuditService",
        "AuthService",
        "GatewayService",
        "ItemService",
    ]
    node_requirements = {
        "GatewayService": {
            "cpu": 1,
            "gpu": 0,
            "ram": 0.75,
            "storage": 0.25,
            "availability": 0.97,
            "processing_time": 6,
        },
        "AuthService": {
            "cpu": 1,
            "gpu": 0,
            "ram": 0.5,
            "storage": 0.25,
            "availability": 0.98,
            "processing_time": 5,
        },
        "ItemService": {
            "cpu": 2,
            "gpu": 0,
            "ram": 1.5,
            "storage": 1.0,
            "availability": 0.95,
            "processing_time": 10,
        },
        "AuditService": {
            "cpu": 1,
            "gpu": 0,
            "ram": 0.5,
            "storage": 0.5,
            "availability": 0.96,
            "processing_time": 4,
        },
    }
    edge_requirements = [
        (
            "GatewayService",
            "AuthService",
            {"symmetric": True, "latency": 12, "bandwidth": 8},
        ),
        (
            "GatewayService",
            "ItemService",
            {"symmetric": True, "latency": 15, "bandwidth": 10},
        ),
        (
            "ItemService",
            "AuditService",
            {"symmetric": True, "latency": 8, "bandwidth": 5},
        ),
        (
            "AuditService",
            "GatewayService",
            {"symmetric": True, "latency": 6, "bandwidth": 4},
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
