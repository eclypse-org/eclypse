import random as rnd

from networkx.classes.reportviews import (
    EdgeView,
    NodeView,
)


def kill_policy(kill_probability: float):
    revive_probability = kill_probability / 2

    def node_update_wrapper(nodes: NodeView):
        for _, resources in nodes.data():
            if rnd.random() < kill_probability:
                resources["availability"] = 0
            elif rnd.random() < revive_probability:
                resources["availability"] = 0.99

    def edge_update_wrapper(_: EdgeView):
        pass

    return node_update_wrapper, edge_update_wrapper
