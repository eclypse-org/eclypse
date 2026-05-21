from __future__ import annotations

import pytest

from eclypse import policies
from tests.unit.policies._helpers import build_graph


def test_failure_policies_target_selected_nodes_and_edges():
    graph = build_graph()

    policies.failure.kill_nodes(1.0, node_ids=["a"])(graph)
    assert graph.nodes["a"]["availability"] == 0.0
    assert graph.nodes["b"]["availability"] == 1.0

    policies.failure.revive_nodes(1.0, node_ids=["a"])(graph)
    assert graph.nodes["a"]["availability"] == 0.99

    graph.nodes["a"]["availability"] = 0.0
    policies.failure.kill_nodes(
        0.0,
        revive_probability=1.0,
        node_ids=["a"],
    )(graph)
    assert graph.nodes["a"]["availability"] == 0.99

    policies.failure.availability_flap(1.0, node_ids=["b"])(graph)
    assert graph.nodes["b"]["availability"] == 0.0

    policies.failure.latency_spike(
        1.0, min_increase=5.0, max_increase=5.0, edge_ids=[("a", "b")]
    )(graph)
    assert graph.edges["a", "b"]["latency"] == 15


def test_failure_policy_validation_and_alternative_branches():
    with pytest.raises(ValueError):
        policies.failure.kill_nodes(1.5)

    with pytest.raises(ValueError):
        policies.failure.availability_flap(-0.1)

    with pytest.raises(ValueError):
        policies.failure.latency_spike(1.0, factor=-1)

    with pytest.raises(ValueError):
        policies.failure.latency_spike(1.0, min_increase=-1)

    with pytest.raises(ValueError):
        policies.failure.latency_spike(1.0, min_increase=2, max_increase=1)

    graph = build_graph()
    graph.nodes["a"]["availability"] = 0.0

    policies.failure.availability_flap(
        0.0,
        up_probability=1.0,
        up_availability=0.75,
        node_ids=["a"],
        unavailable_at_or_below=0.0,
    )(graph)
    assert graph.nodes["a"]["availability"] == 0.75

    policies.failure.latency_spike(1.0, factor=2.0)(graph)
    assert graph.edges["a", "b"]["latency"] == 20

    policies.failure.latency_spike(0.0, factor=2.0)(graph)
    assert graph.edges["a", "b"]["latency"] == 20


def test_edge_and_correlated_failure_policies():
    graph = build_graph()
    graph.edges["a", "b"]["availability"] = 1.0
    graph.nodes["a"]["zone"] = "z1"
    graph.nodes["b"]["zone"] = "z1"

    policies.failure.kill_edges(1.0)(graph)
    assert graph.edges["a", "b"]["availability"] == 0.0

    policies.failure.revive_edges(1.0)(graph)
    assert graph.edges["a", "b"]["availability"] == 1.0

    policies.failure.edge_availability_flap(1.0)(graph)
    assert graph.edges["a", "b"]["availability"] == 0.0

    policies.failure.correlated_failure(1.0, group_key="zone")(graph)
    assert graph.nodes["a"]["availability"] == 0.0
    assert graph.nodes["b"]["availability"] == 0.0


def test_partition_brownout_and_resource_exhaustion_policies():
    graph = build_graph()
    graph.add_node("c", cpu=20, ram=8, availability=1.0)
    graph.add_edge("b", "c", latency=30, bandwidth=50, availability=1.0)
    graph.edges["a", "b"]["availability"] = 1.0

    policies.failure.network_partition([["a"], ["b", "c"]])(graph)
    assert graph.edges["a", "b"]["availability"] == 0.0
    assert graph.edges["b", "c"]["availability"] == 1.0

    removable = build_graph()
    policies.failure.network_partition([["a"], ["b"]], remove_edges=True)(removable)
    assert not removable.has_edge("a", "b")

    policies.failure.resource_exhaustion(1.0, factor=0.5, node_assets="cpu")(graph)
    assert graph.nodes["a"]["cpu"] == 40
    policies.failure.resource_exhaustion(0.0, factor=0.5, node_assets="cpu")(graph)
    assert graph.nodes["a"]["cpu"] == 40

    policies.failure.brownout(1.0, factor=0.5, edge_assets="bandwidth")(graph)
    assert graph.edges["a", "b"]["bandwidth"] == 50

    with pytest.raises(ValueError):
        policies.failure.network_partition([["a"]])
    with pytest.raises(ValueError):
        policies.failure.resource_exhaustion(factor=-1, node_assets="cpu")
    with pytest.raises(ValueError):
        policies.failure.resource_exhaustion()
