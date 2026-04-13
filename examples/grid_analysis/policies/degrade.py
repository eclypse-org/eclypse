from eclypse.graph import AssetGraph


def degrade_value(value, degradation_rate):
    return max(0, value * (1 - degradation_rate))


def degrade_policy(target_degradation: float, epochs: int):
    degradation_rate = 1 - (target_degradation ** (1 / epochs))

    def update_wrapper(graph: AssetGraph):
        for _, resources in graph.nodes.data():
            for key in resources:
                if key in ["cpu", "gpu", "ram", "storage", "availability"]:
                    resources[key] = degrade_value(resources[key], degradation_rate)

        for _, _, resources in graph.edges.data():
            for key in resources:
                resources[key] = degrade_value(resources[key], degradation_rate)

            resources["latency"] = resources["latency"] * (1 + degradation_rate)

            resources["bandwidth"] = degrade_value(
                resources["bandwidth"], degradation_rate
            )

    return update_wrapper
