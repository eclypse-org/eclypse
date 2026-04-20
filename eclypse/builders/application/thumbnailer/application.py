"""Factory for a thumbnailer application."""

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


def get_thumbnailer(
    application_id: str = "Thumbnailer",
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
    """Get the thumbnailer application.

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
            benchmark's built-in media-processing flow.
        store_step (bool):
            Whether instantiated services should store their step outputs in
            the internal step queue. Ignored when
            ``communication_interface`` is ``None``.
        seed (int | None):
            Seed forwarded to the application random generator.

    Returns:
        Application: The configured thumbnailer application.

    Raises:
        ValueError: If ``communication_interface`` is not supported.
    """
    default_flows = [
        [
            "UploadService",
            "TransformService",
            "StorageService",
            "NotificationService",
            "UploadService",
        ]
    ]
    service_names = [
        "NotificationService",
        "StorageService",
        "TransformService",
        "UploadService",
    ]
    node_requirements = {
        "UploadService": {
            "cpu": 0.5,
            "gpu": 0,
            "ram": 0.25,
            "storage": 0.25,
            "availability": 0.98,
            "processing_time": 3,
        },
        "TransformService": {
            "cpu": 2,
            "gpu": 0.5,
            "ram": 1.0,
            "storage": 0.5,
            "availability": 0.96,
            "processing_time": 8,
        },
        "StorageService": {
            "cpu": 1,
            "gpu": 0,
            "ram": 0.5,
            "storage": 1.5,
            "availability": 0.97,
            "processing_time": 5,
        },
        "NotificationService": {
            "cpu": 0.5,
            "gpu": 0,
            "ram": 0.25,
            "storage": 0.1,
            "availability": 0.99,
            "processing_time": 2,
        },
    }
    edge_requirements = [
        (
            "UploadService",
            "TransformService",
            {"symmetric": True, "latency": 8, "bandwidth": 8},
        ),
        (
            "TransformService",
            "StorageService",
            {"symmetric": True, "latency": 10, "bandwidth": 10},
        ),
        (
            "UploadService",
            "StorageService",
            {"symmetric": True, "latency": 9, "bandwidth": 8},
        ),
        (
            "StorageService",
            "NotificationService",
            {"symmetric": True, "latency": 5, "bandwidth": 3},
        ),
        (
            "NotificationService",
            "UploadService",
            {"symmetric": True, "latency": 4, "bandwidth": 2},
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
