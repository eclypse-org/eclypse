from typing import (
    Dict,
    Optional,
)

from eclypse.graph import Application
from eclypse.graph.assets import Asset
from eclypse.utils.types import UpdatePolicies


def get_vas(
    application_id: str = "VAS",
    update_policies: UpdatePolicies = None,
    node_assets: Optional[Dict[str, Asset]] = None,
    edge_assets: Optional[Dict[str, Asset]] = None,
    include_default_assets: bool = True,
    requirement_init: str = "min",
    seed: Optional[int] = None,
) -> Application:
    """Get the Video Analytics Serving (VAS) application."""

    flows = [
        [
            "ObjectDetectionService",
            "ObjectTrackingService",
            "ObjectClassificationService",
        ],  # Object processing flow
        [
            "ObjectDetectionService",
            "ObjectCountingService",
        ],  # Detection and Counting
        [
            "AudioDetectionService",
            "ObjectClassificationService",
        ],  # Audio-visual processing
    ]

    app = Application(
        application_id=application_id,
        update_policies=update_policies,
        node_assets=node_assets,
        edge_assets=edge_assets,
        include_default_assets=include_default_assets,
        requirement_init=requirement_init,
        flows=flows,
        seed=seed,
    )

    app.add_node(
        "ObjectDetectionService",
        cpu=2,
        ram=4.0,
        storage=2.0,
        gpu=2,
        availability=0.95,
        processing_time=15,
    )
    app.add_node(
        "ObjectTrackingService",
        cpu=2,
        ram=3.5,
        storage=1.5,
        gpu=1.5,
        availability=0.94,
        processing_time=20,
    )
    app.add_node(
        "ObjectClassificationService",
        cpu=2,
        ram=4.0,
        storage=2.0,
        gpu=2,
        availability=0.95,
        processing_time=25,
    )
    app.add_node(
        "ObjectCountingService",
        cpu=1,
        ram=2.0,
        storage=1.0,
        gpu=1,
        availability=0.90,
        processing_time=10,
    )
    app.add_node(
        "AudioDetectionService",
        cpu=1,
        ram=1.5,
        storage=0.75,
        gpu=0.5,
        availability=0.90,
        processing_time=8,
    )

    app.add_edge(
        "ObjectDetectionService",
        "ObjectTrackingService",
        symmetric=True,
        latency=30,
        bandwidth=10,
    )
    app.add_edge(
        "ObjectTrackingService",
        "ObjectClassificationService",
        symmetric=True,
        latency=50,
        bandwidth=15,
    )
    app.add_edge(
        "ObjectDetectionService",
        "ObjectCountingService",
        symmetric=True,
        latency=30,
        bandwidth=8,
    )
    app.add_edge(
        "AudioDetectionService",
        "ObjectClassificationService",
        symmetric=True,
        latency=40,
        bandwidth=10,
    )

    return app
