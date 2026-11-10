from __future__ import annotations

import pytest

from eclypse import policies
from eclypse.graph.asset_graph import _normalize_update_policies
from eclypse.policies._filters import (
    apply_numeric_transform,
    clamp,
    coerce_numeric_like,
    ensure_numeric_value,
    iter_selected_edges,
    iter_selected_keys,
    iter_selected_nodes,
)
from eclypse.policies._helpers import validate_missing_behaviour
from eclypse.policies.noise._helpers import apply_additive_walk
from tests.unit.policies._helpers import build_graph


def test_normalize_update_policies_and_filter_helpers_cover_edge_cases():
    def policy(_graph):
        return None

    assert _normalize_update_policies(None) == []
    assert _normalize_update_policies(policy) == [policy]
    assert _normalize_update_policies([policy]) == [policy]

    graph = build_graph()

    assert iter_selected_nodes(
        graph, node_filter=lambda node_id, _: node_id == "a"
    ) == [("a", graph.nodes["a"])]
    assert iter_selected_edges(
        graph,
        edge_filter=lambda source, target, _: (source, target) == ("a", "b"),
    ) == [("a", "b", graph.edges["a", "b"])]
    assert iter_selected_edges(graph, edge_ids=[("missing", "edge")]) == []
    assert (
        iter_selected_edges(
            graph,
            edge_filter=lambda _source, _target, _data: False,
        )
        == []
    )
    assert iter_selected_keys(graph.nodes["a"], ["cpu", "missing"]) == ["cpu"]

    with pytest.raises(TypeError):
        ensure_numeric_value("availability", True)

    with pytest.raises(TypeError):
        ensure_numeric_value("cpu", "busy")

    assert clamp(5, upper=3) == 3
    assert coerce_numeric_like(True, 1.5) == 1.5

    with pytest.raises(ValueError, match="missing"):
        validate_missing_behaviour("skip")


def test_normalise_edges_reaches_total_and_leaves_zero_values_unchanged():
    graph = build_graph()
    policy = policies.constraints.normalise(50, edge_assets="bandwidth")
    policy(graph)
    assert sum(data["bandwidth"] for _, _, data in graph.edges.data()) == 50

    for _, _, data in graph.edges.data():
        data["bandwidth"] = 0
    policy(graph)
    assert all(data["bandwidth"] == 0 for _, _, data in graph.edges.data())


@pytest.mark.parametrize("basis", ["invalid", "initial"])
def test_numeric_helpers_reject_invalid_basis_or_missing_baselines(basis):
    graph = build_graph()
    message = "basis must" if basis == "invalid" else "baselines must"
    with pytest.raises(ValueError, match=message):
        apply_numeric_transform(
            graph,
            node_assets="cpu",
            transform=lambda _key, value: value,
            basis=basis,
            baselines=None,
        )
    with pytest.raises(ValueError, match=message):
        apply_additive_walk(
            graph.nodes["a"],
            {"cpu": 1},
            None,
            delta_sampler=lambda _key, _step: 0,
            basis=basis,
        )


@pytest.mark.parametrize(
    "factory",
    [
        lambda: policies.distribution.constant(node_assets="cpu", basis="invalid"),
        lambda: policies.failure.latency_spike(1, basis="invalid"),
        lambda: policies.noise.impulse(node_assets="cpu", basis="invalid"),
        lambda: policies.workload.diurnal_load(
            amplitude=1, period=4, node_assets="cpu", basis="invalid"
        ),
    ],
)
def test_numeric_policies_reject_invalid_basis_without_mutating_graph(factory):
    graph = build_graph()
    before = {node: dict(data) for node, data in graph.nodes.data()}
    with pytest.raises(ValueError, match="basis must"):
        factory()(graph)
    assert {node: dict(data) for node, data in graph.nodes.data()} == before
