import random as rnd

from networkx.classes.reportviews import (
    EdgeView,
    NodeView,
)


def node_random_update(nodes: NodeView):
    for _, resources in nodes.data():
        if rnd.random() < 0.02:
            resources["availability"] = 0
        elif rnd.random() < 0.5 and resources["availability"] == 0:
            resources["availability"] = 1
        else:
            resources["cpu"] = round(max(0, resources["cpu"] * rnd.uniform(0.95, 1.05)))
            resources["gpu"] = round(max(0, resources["gpu"] * rnd.uniform(0.9, 1.1)))
            resources["ram"] = round(max(0, resources["ram"] * rnd.uniform(0.8, 1.2)))
            resources["storage"] = round(
                max(0, resources["storage"] * rnd.uniform(0.9, 1.1))
            )
            resources["availability"] = min(
                1, max(0, resources["availability"] * rnd.uniform(0.995, 1.005))
            )


def edge_random_update(edges: EdgeView):
    for _, _, resources in edges.data():
        resources["latency"] = round(
            max(0, resources["latency"] * rnd.uniform(0.9, 1.1))
        )
        resources["bandwidth"] = round(
            max(0, resources["bandwidth"] * rnd.uniform(0.95, 1.05))
        )
