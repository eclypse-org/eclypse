from __future__ import annotations

import pytest

from eclypse.graph.asset_graph import AssetGraph
from eclypse.graph.assets import Additive
from eclypse.graph.infrastructure import (
    Infrastructure,
    _cost_changed,
    _default_weight_function,
)
from eclypse.placement.strategies import StaticStrategy


def test_infrastructure_path_resources_and_cache_behaviour(sample_infrastructure):
    path = sample_infrastructure.path("edge-a", "edge-b")

    assert path == [
        ("edge-a", "edge-b", sample_infrastructure.edges["edge-a", "edge-b"])
    ]
    assert sample_infrastructure.processing_time("edge-a", "edge-b") == 5
    assert sample_infrastructure.path_resources("edge-a", "edge-b") == {
        "latency": 5,
        "bandwidth": 10,
    }
    assert sample_infrastructure.path("edge-a", "missing") is None

    sample_infrastructure.nodes["edge-b"]["availability"] = 0
    assert "edge-b" not in sample_infrastructure.available

    sample_infrastructure.remove_edge("edge-a", "edge-b")
    assert sample_infrastructure.path("edge-a", "edge-b") is None


def test_infrastructure_evolve_invalidates_cached_path_resources(sample_infrastructure):
    assert sample_infrastructure.path_resources("edge-a", "edge-b")["bandwidth"] == 10

    sample_infrastructure.update_policies = [
        lambda graph: graph.edges["edge-a", "edge-b"].update(bandwidth=5)
    ]

    sample_infrastructure.evolve()

    assert sample_infrastructure.path_resources("edge-a", "edge-b")["bandwidth"] == 5


def test_infrastructure_requires_path_aggregators_for_custom_edge_assets():
    with pytest.raises(ValueError, match='path asset aggregator for "bandwidth"'):
        Infrastructure(
            edge_assets={"bandwidth": Additive(0, 10)},
            include_default_assets=False,
        )


def test_infrastructure_contains_and_helper_functions(sample_infrastructure):
    requirements = AssetGraph(
        "requirements",
        node_assets=sample_infrastructure.node_assets,
        edge_assets=sample_infrastructure.edge_assets,
    )
    requirements.add_node("edge-a", cpu=100)
    requirements.add_node("edge-b", cpu=1)
    requirements.add_edge("edge-a", "edge-b", latency=0, bandwidth=1000, strict=False)

    not_respected = sample_infrastructure.contains(requirements)

    assert "edge-a" in not_respected
    assert "edge-b" in not_respected
    assert _default_weight_function("u", "v", {"latency": 4}) == 4
    assert _cost_changed(10, 0)


def test_infrastructure_same_node_resources_and_strategy_flag(sample_infrastructure):
    assert sample_infrastructure.path_resources("edge-a", "edge-a") == (
        sample_infrastructure.edge_assets.upper_bound
    )
    assert sample_infrastructure.processing_time("edge-a", "edge-a") == 0.0
    assert sample_infrastructure.has_strategy is False

    sample_infrastructure.strategy = StaticStrategy({"gateway": "edge-a"})

    assert sample_infrastructure.has_strategy is True
