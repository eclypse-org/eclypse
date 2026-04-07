from __future__ import annotations

import pytest

from eclypse.graph import Application
from eclypse.graph.asset_graph import AssetGraph
from eclypse.graph.assets import Additive
from eclypse.graph.infrastructure import (
    Infrastructure,
    _cost_changed,
    _default_weight_function,
)
from eclypse.remote.service.service import Service


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
        node_update_policy=lambda nodes: nodes["a"].update(cpu=nodes["a"]["cpu"] + 1),
        edge_update_policy=lambda edges: edges["a", "b"].update(
            bandwidth=edges["a", "b"]["bandwidth"] + 1
        ),
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


def test_application_add_service_and_set_flows():
    app = Application("demo")
    gateway = Service("gateway")
    worker = Service("worker")

    app.add_service(gateway)
    app.add_service(worker)
    app.add_edge("gateway", "worker")
    app.set_flows()

    assert app.flows == [["gateway", "worker"]]
    assert app.has_logic

    with pytest.raises(TypeError):
        app.add_service("not-a-service")  # type: ignore[arg-type]


def test_application_detects_missing_service_logic():
    app = Application("broken")
    app.add_node("orphan")

    assert not app.has_logic


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
