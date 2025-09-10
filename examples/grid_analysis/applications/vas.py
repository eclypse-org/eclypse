from typing import (
    Callable,
    Dict,
    Optional,
)

from networkx.classes.reportviews import (
    EdgeView,
    NodeView,
)

from eclypse.graph import (
    Application,
    NodeGroup,
)
from eclypse.graph.assets import Asset


def get_vas(
    application_id: str = "VAS",
    node_update_policy: Optional[Callable[[NodeView], None]] = None,
    edge_update_policy: Optional[Callable[[EdgeView], None]] = None,
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
        node_update_policy=node_update_policy,
        edge_update_policy=edge_update_policy,
        node_assets=node_assets,
        edge_assets=edge_assets,
        include_default_assets=include_default_assets,
        requirement_init=requirement_init,
        flows=flows,
        seed=seed,
    )

    app.add_node_by_group(
        NodeGroup.NEAR_EDGE,
        "ObjectDetectionService",
        cpu=2,
        ram=4.0,
        storage=2.0,
        gpu=2,
        availability=0.95,
        processing_time=15,
    )
    app.add_node_by_group(
        NodeGroup.NEAR_EDGE,
        "ObjectTrackingService",
        cpu=2,
        ram=3.5,
        storage=1.5,
        gpu=1.5,
        availability=0.94,
        processing_time=20,
    )
    app.add_node_by_group(
        NodeGroup.NEAR_EDGE,
        "ObjectClassificationService",
        cpu=2,
        ram=4.0,
        storage=2.0,
        gpu=2,
        availability=0.95,
        processing_time=25,
    )
    app.add_node_by_group(
        NodeGroup.IOT,
        "ObjectCountingService",
        cpu=1,
        ram=2.0,
        storage=1.0,
        gpu=1,
        availability=0.90,
        processing_time=10,
    )
    app.add_node_by_group(
        NodeGroup.IOT,
        "AudioDetectionService",
        cpu=1,
        ram=1.5,
        storage=0.75,
        gpu=0.5,
        availability=0.90,
        processing_time=8,
    )

    app.add_edge_by_group(
        "ObjectDetectionService",
        "ObjectTrackingService",
        symmetric=True,
        latency=30,
        bandwidth=10,
    )
    app.add_edge_by_group(
        "ObjectTrackingService",
        "ObjectClassificationService",
        symmetric=True,
        latency=50,
        bandwidth=15,
    )
    app.add_edge_by_group(
        "ObjectDetectionService",
        "ObjectCountingService",
        symmetric=True,
        latency=30,
        bandwidth=8,
    )
    app.add_edge_by_group(
        "AudioDetectionService",
        "ObjectClassificationService",
        symmetric=True,
        latency=40,
        bandwidth=10,
    )

    return app
