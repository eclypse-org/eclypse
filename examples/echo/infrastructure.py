from update_policy import (
    edge_random_update,
    node_random_update,
)

from eclypse.graph import Infrastructure, NodeGroup


# Creating an instance of the Infrastructure class
def get_infrastructure(seed: int = 2) -> Infrastructure:
    echo_infra = Infrastructure(
        "EchoInfrastructure",
        node_update_policy=node_random_update,
        edge_update_policy=edge_random_update,
        seed=seed,
    )
    echo_infra.add_node_by_group(NodeGroup.CLOUD, "CloudServer")
    echo_infra.add_node_by_group(NodeGroup.FAR_EDGE, "EdgeGateway")
    echo_infra.add_node_by_group(NodeGroup.IOT, "IoTDevice")
    echo_infra.add_node_by_group(NodeGroup.CLOUD, "CloudStorage")
    echo_infra.add_node_by_group(NodeGroup.NEAR_EDGE, "EdgeSensor")

    echo_infra.add_symmetric_edge(
        "CloudServer", "EdgeGateway", latency=5.0, bandwidth=80.0
    )
    echo_infra.add_symmetric_edge(
        "EdgeGateway", "IoTDevice", latency=8.0, bandwidth=50.0
    )
    echo_infra.add_symmetric_edge(
        "IoTDevice", "CloudStorage", latency=15.0, bandwidth=100.0
    )
    echo_infra.add_symmetric_edge(
        "CloudStorage", "EdgeSensor", latency=9.0, bandwidth=70.0
    )

    return echo_infra
