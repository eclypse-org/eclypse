import random as rnd

from eclypse.graph import AssetGraph


def kill_policy(kill_probability: float):
    revive_probability = kill_probability / 2

    def update_wrapper(graph: AssetGraph):
        for _, resources in graph.nodes.data():
            if rnd.random() < kill_probability:
                resources["availability"] = 0
            elif rnd.random() < revive_probability:
                resources["availability"] = 0.99

    return update_wrapper
