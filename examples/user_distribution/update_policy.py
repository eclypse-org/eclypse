import random as rnd
from pathlib import Path

import pandas as pd
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

    return node_update_wrapper


class EdgeUpdatePolicy:
    def __init__(self, kill_probability: float):
        self.initial_latencies = None
        self.kill_probability = kill_probability
        self.revive_probability = kill_probability / 2

    def __call__(self, edges: EdgeView):
        if self.initial_latencies is None:
            self.initial_latencies = {
                (u, v): data["latency"] for u, v, data in edges.data()
            }

        for u, v, data in edges.data():
            if rnd.random() < self.kill_probability:
                data["latency"] += rnd.randint(1, 5)
            elif rnd.random() < self.revive_probability:
                data["latency"] = self.initial_latencies[(u, v)]


class UserDistributionPolicy:
    def __init__(self):
        self.df = pd.read_parquet(Path(__file__).parent / "dataset.parquet")
        self.df = self.df.astype({"node_id": int, "time": int, "user_count": int})

        self.step = self.df["time"].min()
        self.factor = 1

    def __call__(self, nodes: NodeView):

        if self.step == 1000 or self.step == 3000:
            self.factor += 2
        elif self.step == 2000 or self.step == 4000:
            self.factor -= 2

        current_data = self.df[self.df["time"] == self.step]
        for _, row in current_data.iterrows():
            user_count = int(row["user_count"]) * self.factor
            nodes[row["node_id"]]["user_count"] = user_count

        self.step += 1
