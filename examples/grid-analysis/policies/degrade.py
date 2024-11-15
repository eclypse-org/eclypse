from networkx.classes.reportviews import (
    EdgeView,
    NodeView,
)


def degrade_value(value, degradation_rate):
    return max(0, value * (1 - degradation_rate))


def degrade_policy(target_degradation: float, epochs: int):
    degradation_rate = 1 - (target_degradation ** (1 / epochs))

    def node_update_wrapper(nodes: NodeView):
        for _, resources in nodes.data():
            for key in resources:
                if key in ["cpu", "gpu", "ram", "storage", "availability"]:
                    resources[key] = degrade_value(resources[key], degradation_rate)

    def edge_update_wrapper(edges: EdgeView):
        for _, _, resources in edges.data():
            for key in resources:
                resources[key] = degrade_value(resources[key], degradation_rate)

            resources["latency"] = resources["latency"] * (1 + degradation_rate)

            resources["bandwidth"] = degrade_value(
                resources["bandwidth"], degradation_rate
            )

    return node_update_wrapper, edge_update_wrapper
