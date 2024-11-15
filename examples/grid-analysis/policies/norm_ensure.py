import random as rnd

import networkx as nx
from networkx.classes.reportviews import (
    EdgeView,
    NodeView,
)
from scipy.stats import norm

from eclypse.graph import NodeGroup as ng


def normal_update(value, mean, std_dev):
    return round(max(0, value * norm.rvs(loc=mean, scale=std_dev)))


group_params = {
    ng.CLOUD: {
        "cpu": (1.0, 0.05),
        "gpu": (1.0, 0.1),
        "ram": (1.0, 0.15),
        "storage": (1.0, 0.1),
    },
    ng.FAR_EDGE: {
        "cpu": (0.95, 0.1),
        "gpu": (0.9, 0.15),
        "ram": (0.85, 0.2),
        "storage": (0.9, 0.15),
    },
    ng.NEAR_EDGE: {
        "cpu": (0.9, 0.1),
        "gpu": (0.85, 0.2),
        "ram": (0.8, 0.25),
        "storage": (0.85, 0.2),
    },
    ng.IOT: {
        "cpu": (0.85, 0.15),
        "gpu": (0.8, 0.25),
        "ram": (0.75, 0.3),
        "storage": (0.8, 0.25),
    },
}


def ensure_policy(node_reqs: dict, path_reqs: dict):
    def node_update_wrapper(nodes: NodeView):

        aggregated_reqs = {}
        for key, value in node_reqs.items():
            aggregated_reqs[key] = (
                max(aggregated_reqs[key], value) if key in aggregated_reqs else value
            )

        for _, resources in nodes.data():
            group = resources.get("group", ng.CLOUD)
            params = group_params.get(group, group_params[ng.CLOUD])

            # ensure for current node
            for key, value in aggregated_reqs.items():
                resources[key] = max(resources.get(key, 0), value)

            # update following normal distribution
            for key in resources:
                if key not in aggregated_reqs:
                    if key in params:
                        mean, std_dev = params[key]
                        resources[key] = normal_update(resources[key], mean, std_dev)
                    elif key == "availability":
                        resources[key] = min(
                            1, max(0, resources[key] * rnd.uniform(0.995, 1.005))
                        )

    def edge_update_wrapper(edges: EdgeView):
        min_bandwidth = path_reqs.get("bandwidth", 0)
        max_latency = path_reqs.get("latency", float("inf"))

        for u, v, resources in edges.data():
            # Ensure the link's bandwidth meets the minimum bandwidth requirement
            resources["bandwidth"] = max(resources.get("bandwidth", 0), min_bandwidth)

            # Ensure the link's latency meets the maximum latency requirement
            resources["latency"] = min(
                resources.get("latency", float("inf")), max_latency
            )

        # Check if all paths meet the cumulative latency and minimum bandwidth requirements
        graph = edges._graph
        all_paths = dict(nx.all_pairs_dijkstra_path(graph, weight="latency"))

        for source, paths in all_paths.items():
            for target, path in paths.items():
                if source != target:
                    cumulative_latency = sum(
                        graph[u][v]["latency"] for u, v in zip(path[:-1], path[1:])
                    )
                    if cumulative_latency > max_latency:
                        # Adjust latencies to ensure the path meets the requirement
                        adjustment_factor = max_latency / cumulative_latency
                        for u, v in zip(path[:-1], path[1:]):
                            graph[u][v]["latency"] *= adjustment_factor
                    for u, v in zip(path[:-1], path[1:]):
                        # Ensure each link in the path meets the minimum bandwidth requirement
                        graph[u][v]["bandwidth"] = min(
                            graph[u][v]["bandwidth"], min_bandwidth
                        )

    return node_update_wrapper, edge_update_wrapper
