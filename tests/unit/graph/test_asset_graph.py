from __future__ import annotations

import pytest

from eclypse.graph.asset_graph import AssetGraph
from eclypse.graph.assets import Additive


def test_asset_graph_validates_nodes_edges_and_dynamic_flags():
    graph = AssetGraph(
        "assets",
        node_assets={"cpu": Additive(0, 10)},
        edge_assets={"bandwidth": Additive(0, 10)},
    )

    graph.add_node("a", cpu=5)
    graph.add_node("b", cpu=6)
    graph.add_edge("a", "b", bandwidth=4, symmetric=True)

    assert graph.has_edge("b", "a")
    assert not graph.is_dynamic

    with pytest.raises(ValueError):
        graph.add_node("c", cpu=11)

    with pytest.raises(ValueError):
        graph.add_edge("missing", "a", bandwidth=1)


def test_asset_graph_evolve_runs_registered_policies():
    graph = AssetGraph(
        "dynamic",
        update_policies=[
            lambda graph: graph.nodes["a"].update(cpu=graph.nodes["a"]["cpu"] + 1),
            lambda graph: graph.edges["a", "b"].update(
                bandwidth=graph.edges["a", "b"]["bandwidth"] + 1
            ),
        ],
        node_assets={"cpu": Additive(0, 10)},
        edge_assets={"bandwidth": Additive(0, 10)},
    )
    graph.add_node("a", cpu=1)
    graph.add_node("b", cpu=1)
    graph.add_edge("a", "b", bandwidth=2)

    graph.evolve()

    assert graph.nodes["a"]["cpu"] == 2
    assert graph.edges["a", "b"]["bandwidth"] == 3
    assert graph.is_dynamic
