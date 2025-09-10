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


def get_assembly_platform(
    application_id: str = "AssemblyPlatform",
    node_update_policy: Optional[Callable[[NodeView], None]] = None,
    edge_update_policy: Optional[Callable[[EdgeView], None]] = None,
    node_assets: Optional[Dict[str, Asset]] = None,
    edge_assets: Optional[Dict[str, Asset]] = None,
    include_default_assets: bool = True,
    requirement_init: str = "min",
    seed: Optional[int] = None,
) -> Application:
    """Get the Assembly Platform application."""

    flows = [
        [
            "ProductStructuralModel",
            "AssemblyTaskOrchestration",
            "ResourceDiscovery",
            "CompositeAssembly",
            "PrimitiveAssembly",
            "StateTracking",
        ],  # Dynamic Assembly Process Generation
        [
            "StateTracking",
            "QualityMonitoring",
            "AssemblyWorkerCoordination",
            "IoTWrapper",
        ],  # Real-Time Quality Assurance
        [
            "AssemblyWorkerCoordination",
            "IoTWrapper",
            "PrimitiveAssembly",
        ],  # Adaptive Assembly Worker Coordination
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
        NodeGroup.FAR_EDGE,
        "AssemblyTaskOrchestration",
        cpu=2,
        gpu=0,
        ram=4.0,
        storage=2.0,
        availability=0.9,
        processing_time=15,
    )
    app.add_node_by_group(
        NodeGroup.CLOUD,
        "ProductStructuralModel",
        cpu=2,
        gpu=0,
        ram=3.0,
        storage=1.5,
        availability=0.9,
        processing_time=20,
    )
    app.add_node_by_group(
        NodeGroup.IOT,
        "PrimitiveAssembly",
        cpu=1,
        gpu=0.5,
        ram=1.0,
        storage=0.5,
        availability=0.9,
        processing_time=10,
    )
    app.add_node_by_group(
        NodeGroup.NEAR_EDGE,
        "CompositeAssembly",
        cpu=2,
        gpu=1.5,
        ram=3.0,
        storage=1.0,
        availability=0.9,
        processing_time=25,
    )
    app.add_node_by_group(
        NodeGroup.IOT,
        "IoTWrapper",
        cpu=1,
        gpu=0,
        ram=0.75,
        storage=0.5,
        availability=0.9,
        processing_time=8,
    )
    app.add_node_by_group(
        NodeGroup.CLOUD,
        "ResourceDiscovery",
        cpu=2,
        gpu=0,
        ram=2.0,
        storage=1.5,
        availability=0.9,
        processing_time=12,
    )
    app.add_node_by_group(
        NodeGroup.NEAR_EDGE,
        "QualityMonitoring",
        cpu=1,
        gpu=0.5,
        ram=1.5,
        storage=0.75,
        availability=0.9,
        processing_time=10,
    )
    app.add_node_by_group(
        NodeGroup.FAR_EDGE,
        "AssemblyWorkerCoordination",
        cpu=2,
        gpu=0,
        ram=2.5,
        storage=1.0,
        availability=0.9,
        processing_time=15,
    )
    app.add_node_by_group(
        NodeGroup.IOT,
        "StateTracking",
        cpu=1,
        gpu=0.5,
        ram=1.0,
        storage=0.5,
        availability=0.9,
        processing_time=10,
    )

    app.add_edge_by_group(
        "AssemblyTaskOrchestration",
        "ProductStructuralModel",
        symmetric=True,
        latency=100,
        bandwidth=5,
    )
    app.add_edge_by_group(
        "AssemblyTaskOrchestration",
        "CompositeAssembly",
        symmetric=True,
        latency=50,
        bandwidth=10,
    )
    app.add_edge_by_group(
        "CompositeAssembly",
        "PrimitiveAssembly",
        symmetric=True,
        latency=40,
        bandwidth=20,
    )
    app.add_edge_by_group(
        "IoTWrapper",
        "AssemblyWorkerCoordination",
        symmetric=True,
        latency=40,
        bandwidth=8,
    )
    app.add_edge_by_group(
        "ResourceDiscovery",
        "AssemblyTaskOrchestration",
        symmetric=True,
        latency=120,
        bandwidth=3,
    )
    app.add_edge_by_group(
        "QualityMonitoring",
        "StateTracking",
        symmetric=True,
        latency=40,
        bandwidth=2,
    )
    app.add_edge_by_group(
        "AssemblyWorkerCoordination",
        "IoTWrapper",
        symmetric=True,
        latency=40,
        bandwidth=7,
    )

    return app
