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
