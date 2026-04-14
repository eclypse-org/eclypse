from __future__ import annotations

from eclypse.graph.asset_graph import AssetGraph
from eclypse.graph.assets import Additive


class FakeDataFrame:
    def __init__(self, records):
        self._records = records

    def to_dict(self, orient: str):
        assert orient == "records"
        return self._records


class IterRowsFrame:
    def __init__(self, records):
        self._records = records

    def iterrows(self):
        yield from enumerate(self._records)


def build_graph(seed: int = 7) -> AssetGraph:
    graph = AssetGraph(
        "dynamic",
        seed=seed,
        node_assets={
            "cpu": Additive(0, 1000),
            "ram": Additive(0, 1000),
            "availability": Additive(0, 1),
        },
        edge_assets={
            "latency": Additive(0, 10_000),
            "bandwidth": Additive(0, 10_000),
        },
    )
    graph.add_node("a", cpu=80, ram=32, availability=1.0)
    graph.add_node("b", cpu=50, ram=16, availability=1.0)
    graph.add_edge("a", "b", latency=10, bandwidth=100)
    return graph
