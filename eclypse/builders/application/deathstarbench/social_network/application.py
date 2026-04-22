"""Factory for a social network microservice application."""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Literal,
)

from eclypse.builders.application._helpers import build_application_from_specs

if TYPE_CHECKING:
    from eclypse.graph import Application
    from eclypse.graph.assets import Asset
    from eclypse.utils.types import (
        CommunicationInterface,
        InitPolicy,
        UpdatePolicies,
    )


def get_social_network(
    application_id: str = "SocialNetwork",
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
    """Get the social network application.

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
            benchmark's built-in posting and timeline flows.
        store_step (bool):
            Whether instantiated services should store their step outputs in
            the internal step queue. Ignored when
            ``communication_interface`` is ``None``.
        seed (int | None):
            Seed forwarded to the application random generator.

    Returns:
        Application: The configured social network application.

    Raises:
        ValueError: If ``communication_interface`` is not supported.
    """
    default_flows = [
        [
            "ComposePostService",
            "UniqueIdService",
            "TextService",
            "UserMentionService",
            "UrlShortenService",
            "MediaService",
            "UserService",
            "PostStorageService",
            "UserTimelineService",
            "HomeTimelineService",
            "SocialGraphService",
            "HomeTimelineService",
            "ComposePostService",
        ],
        ["UserTimelineService", "PostStorageService", "UserTimelineService"],
        ["HomeTimelineService", "PostStorageService", "HomeTimelineService"],
    ]
    service_names = [
        "ComposePostService",
        "UniqueIdService",
        "TextService",
        "UserMentionService",
        "UrlShortenService",
        "MediaService",
        "UserService",
        "PostStorageService",
        "UserTimelineService",
        "HomeTimelineService",
        "SocialGraphService",
    ]
    node_requirements = {
        "ComposePostService": {
            "cpu": 2,
            "gpu": 0,
            "ram": 1.75,
            "storage": 0.5,
            "availability": 0.94,
            "processing_time": 16,
        },
        "UniqueIdService": {
            "cpu": 1,
            "gpu": 0,
            "ram": 0.25,
            "storage": 0.25,
            "availability": 0.98,
            "processing_time": 4,
        },
        "TextService": {
            "cpu": 1,
            "gpu": 0,
            "ram": 0.75,
            "storage": 0.25,
            "availability": 0.96,
            "processing_time": 6,
        },
        "UserMentionService": {
            "cpu": 1,
            "gpu": 0,
            "ram": 0.5,
            "storage": 0.25,
            "availability": 0.96,
            "processing_time": 5,
        },
        "UrlShortenService": {
            "cpu": 1,
            "gpu": 0,
            "ram": 1.0,
            "storage": 0.75,
            "availability": 0.95,
            "processing_time": 8,
        },
        "MediaService": {
            "cpu": 2,
            "gpu": 0,
            "ram": 1.75,
            "storage": 1.5,
            "availability": 0.93,
            "processing_time": 11,
        },
        "UserService": {
            "cpu": 1,
            "gpu": 0,
            "ram": 1.25,
            "storage": 1.0,
            "availability": 0.94,
            "processing_time": 9,
        },
        "PostStorageService": {
            "cpu": 3,
            "gpu": 0,
            "ram": 2.5,
            "storage": 3.0,
            "availability": 0.91,
            "processing_time": 13,
        },
        "UserTimelineService": {
            "cpu": 2,
            "gpu": 0,
            "ram": 2.0,
            "storage": 1.75,
            "availability": 0.92,
            "processing_time": 11,
        },
        "HomeTimelineService": {
            "cpu": 2,
            "gpu": 0,
            "ram": 2.0,
            "storage": 1.75,
            "availability": 0.92,
            "processing_time": 12,
        },
        "SocialGraphService": {
            "cpu": 2,
            "gpu": 0,
            "ram": 1.5,
            "storage": 1.5,
            "availability": 0.93,
            "processing_time": 10,
        },
    }
    edge_requirements = [
        (
            "ComposePostService",
            "UniqueIdService",
            {"symmetric": True, "latency": 12, "bandwidth": 8},
        ),
        (
            "UniqueIdService",
            "TextService",
            {"symmetric": True, "latency": 10, "bandwidth": 8},
        ),
        (
            "TextService",
            "UserMentionService",
            {"symmetric": True, "latency": 10, "bandwidth": 6},
        ),
        (
            "UserMentionService",
            "UrlShortenService",
            {"symmetric": True, "latency": 12, "bandwidth": 6},
        ),
        (
            "UrlShortenService",
            "MediaService",
            {"symmetric": True, "latency": 14, "bandwidth": 12},
        ),
        (
            "MediaService",
            "UserService",
            {"symmetric": True, "latency": 12, "bandwidth": 10},
        ),
        (
            "UserService",
            "PostStorageService",
            {"symmetric": True, "latency": 14, "bandwidth": 14},
        ),
        (
            "PostStorageService",
            "UserTimelineService",
            {"symmetric": True, "latency": 16, "bandwidth": 14},
        ),
        (
            "UserTimelineService",
            "HomeTimelineService",
            {"symmetric": True, "latency": 14, "bandwidth": 12},
        ),
        (
            "HomeTimelineService",
            "SocialGraphService",
            {"symmetric": True, "latency": 12, "bandwidth": 10},
        ),
        (
            "HomeTimelineService",
            "ComposePostService",
            {"symmetric": True, "latency": 12, "bandwidth": 8},
        ),
        (
            "UserTimelineService",
            "PostStorageService",
            {"symmetric": True, "latency": 14, "bandwidth": 14},
        ),
        (
            "HomeTimelineService",
            "PostStorageService",
            {"symmetric": True, "latency": 14, "bandwidth": 14},
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
