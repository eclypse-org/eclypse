from __future__ import annotations

import random as rnd
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from networkx.classes.reportviews import NodeView


def kill_policy(kill_probability: float):
    revive_probability = kill_probability / 2

    def node_update_wrapper(nodes: NodeView):
        for n, resources in nodes.data():
            if rnd.random() < kill_probability and resources["availability"] > 0:
                resources["availability"] = 0
                print(f"Killed node {n}")
            elif rnd.random() < revive_probability and resources["availability"] == 0:
                resources["availability"] = 0.99
                # print(f"Revived node {n}")

    return node_update_wrapper


__all__ = ["kill_policy"]
