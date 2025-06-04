from typing import (
    Callable,
    Dict,
    Optional,
)

from networkx.classes.reportviews import (
    EdgeView,
    NodeView,
)

from eclypse.graph import Application
from eclypse.graph.assets import Asset


def get_health_guardian(
    application_id: str = "HealthGuardian",
    node_update_policy: Optional[Callable[[NodeView], None]] = None,
    edge_update_policy: Optional[Callable[[EdgeView], None]] = None,
    node_assets: Optional[Dict[str, Asset]] = None,
    edge_assets: Optional[Dict[str, Asset]] = None,
    include_default_assets: bool = True,
    requirement_init: str = "min",
    seed: Optional[int] = None,
) -> Application:
    """Get the Health Guardian application."""

    flows = [
        [
            "DepressionAssessment",
            "MobilityAnalysis",
            "FunctionalMobility",
        ],  # Mental Health Monitoring
        [
            "ALSVoiceAnalysis",
            "CognitiveDeclineDetection",
            "MobilityAnalysis",
            "FunctionalMobility",
        ],  # Neurodegenerative Disease Monitoring
        [
            "CognitiveDeclineDetection",
            "DepressionAssessment",
            "DrivingRiskAssessment",
            "SleepQuality",
        ],  # Comprehensive Health Assessment
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

    app.add_node(
        "DepressionAssessment",
        cpu=1,
        gpu=0,
        ram=0.5,
        storage=0.3,
        availability=0.95,
        processing_time=5,
    ),

    app.add_node(
        "MobilityAnalysis",
        cpu=2,
        gpu=0.5,
        ram=1.0,
        storage=0.5,
        availability=0.93,
        processing_time=15,
    ),

    app.add_node(
        "FunctionalMobility",
        cpu=1,
        gpu=1,
        ram=1.5,
        storage=0.75,
        availability=0.92,
        processing_time=10,
    ),

    app.add_node(
        "ALSVoiceAnalysis",
        cpu=2,
        gpu=1.5,
        ram=1.5,
        storage=1.0,
        availability=0.94,
        processing_time=20,
    ),

    app.add_node(
        "CognitiveDeclineDetection",
        cpu=3,
        gpu=2,
        ram=2.5,
        storage=1.5,
        availability=0.93,
        processing_time=25,
    ),

    app.add_node(
        "SleepQuality",
        cpu=1,
        gpu=0.5,
        ram=1.0,
        storage=0.5,
        availability=0.95,
        processing_time=8,
    ),

    app.add_node(
        "DrivingRiskAssessment",
        cpu=2,
        gpu=1,
        ram=1.5,
        storage=0.75,
        availability=0.90,
        processing_time=12,
    ),

    app.add_edge(
        "DepressionAssessment",
        "MobilityAnalysis",
        symmetric=True,
        latency=35,
        bandwidth=5,
    )
    app.add_edge(
        "MobilityAnalysis",
        "FunctionalMobility",
        symmetric=True,
        latency=40,
        bandwidth=10,
    )
    app.add_edge(
        "ALSVoiceAnalysis",
        "CognitiveDeclineDetection",
        symmetric=True,
        latency=50,
        bandwidth=8,
    )
    app.add_edge(
        "CognitiveDeclineDetection",
        "SleepQuality",
        symmetric=True,
        latency=45,
        bandwidth=6,
    )
    app.add_edge(
        "DrivingRiskAssessment",
        "CognitiveDeclineDetection",
        symmetric=True,
        latency=35,
        bandwidth=7,
    )

    return app
