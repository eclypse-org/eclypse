from update_policy import (
    edge_random_update,
    node_random_update,
)

from eclypse.graph import Infrastructure


# Creating an instance of the Infrastructure class
def get_infrastructure(seed: int = 2) -> Infrastructure:
    echo_infra = Infrastructure(
        "EchoInfrastructure",
        node_update_policy=node_random_update,
        edge_update_policy=edge_random_update,
        include_default_assets=True,
        seed=seed,
    )
    echo_infra.add_node("CloudServer")
    echo_infra.add_node("EdgeGateway")
    echo_infra.add_node("IoTDevice")
    echo_infra.add_node("CloudStorage")
    echo_infra.add_node("EdgeSensor")

    echo_infra.add_edge(
        "CloudServer", "EdgeGateway", latency=5.0, bandwidth=80.0, symmetric=True
    )
    echo_infra.add_edge(
        "EdgeGateway", "IoTDevice", latency=8.0, bandwidth=50.0, symmetric=True
    )
    echo_infra.add_edge(
        "IoTDevice", "CloudStorage", latency=15.0, bandwidth=100.0, symmetric=True
    )
    echo_infra.add_edge(
        "CloudStorage", "EdgeSensor", latency=9.0, bandwidth=70.0, symmetric=True
    )

    return echo_infra
