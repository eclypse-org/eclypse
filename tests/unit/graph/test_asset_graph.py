from __future__ import annotations

import pytest

import eclypse.graph.asset_graph as asset_graph_module
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


def test_asset_graph_handles_invalid_init_and_non_strict_violations(monkeypatch):
    messages: list[tuple[str, str]] = []
    traces: list[dict[str, object]] = []

    class DummyBoundLogger:
        def warning(self, message: str):
            messages.append(("warning", message))

        def debug(self, message: str):
            messages.append(("debug", message))

        def trace(self, message: str):
            messages.append(("trace", message))

    class DummyLogger:
        def bind(self, **_kwargs):
            return DummyBoundLogger()

    monkeypatch.setattr(asset_graph_module, "logger", DummyLogger())
    monkeypatch.setattr(
        asset_graph_module,
        "log_assets_violations",
        lambda _logger, _bucket, violations: traces.append(violations),
    )

    with pytest.raises(ValueError, match="attr_init can be 'min' or 'max'"):
        AssetGraph("invalid", attr_init="mid")  # type: ignore[arg-type]

    graph = AssetGraph(
        "warnings",
        node_assets={"cpu": Additive(0, 10)},
        edge_assets={"bandwidth": Additive(0, 10)},
        update_policies=[lambda current: current.nodes["a"].update(cpu=2)],
    )
    graph.add_node("a", cpu=11, strict=False)
    graph.add_node("b", cpu=2)
    graph.add_edge("a", "b", bandwidth=11, strict=False)
    graph.evolve()

    assert any("a has inconsistent assets" in message for _, message in messages)
    assert any(
        "(a -> b) has inconsistent assets" in message for _, message in messages
    )
    assert any("Applying 1 update policies." in message for _, message in messages)
    assert traces == [
        {"cpu": 11},
        {"bandwidth": 11},
    ]


def test_asset_graph_rejects_missing_edge_target():
    graph = AssetGraph(
        "targets",
        node_assets={"cpu": Additive(0, 10)},
        edge_assets={"bandwidth": Additive(0, 10)},
    )
    graph.add_node("a", cpu=5)

    with pytest.raises(ValueError, match="Node b not found in the graph"):
        graph.add_edge("a", "b", bandwidth=1)


def test_asset_graph_rejects_strict_edge_violations_and_allows_static_evolve():
    graph = AssetGraph(
        "strict-edge",
        node_assets={"cpu": Additive(0, 10)},
        edge_assets={"bandwidth": Additive(0, 10)},
    )
    graph.add_node("a", cpu=1)
    graph.add_node("b", cpu=2)

    with pytest.raises(ValueError, match=r"\(a -> b\) has inconsistent assets"):
        graph.add_edge("a", "b", bandwidth=11)

    graph.evolve()


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
