from __future__ import annotations

import pytest

from eclypse import policies
from tests.unit.policies._helpers import build_graph


def test_degradation_policies_stop_at_the_requested_epoch():
    graph = build_graph()

    reduce = policies.degradation.reduce_capacity(
        0.25,
        2,
        node_assets="cpu",
        edge_assets="bandwidth",
    )
    latency = policies.degradation.increase_latency(target=40, epochs=2)

    reduce(graph)
    latency(graph)
    assert graph.nodes["a"]["cpu"] == 40
    assert graph.edges["a", "b"]["bandwidth"] == 50
    assert graph.edges["a", "b"]["latency"] == 20

    reduce(graph)
    latency(graph)
    assert graph.nodes["a"]["cpu"] == 20
    assert graph.edges["a", "b"]["bandwidth"] == 25
    assert graph.edges["a", "b"]["latency"] == 40


def test_degradation_validation_and_rate_mode():
    with pytest.raises(ValueError):
        policies.degradation.reduce_capacity(0.5, 0)

    with pytest.raises(ValueError):
        policies.degradation.degrade(0.0, 2)

    with pytest.raises(ValueError):
        policies.degradation.increase_latency()

    with pytest.raises(ValueError):
        policies.degradation.increase_latency(rate=0.1, target=20, epochs=2)

    with pytest.raises(ValueError):
        policies.degradation.increase_latency(rate=-2.0)

    with pytest.raises(ValueError):
        policies.degradation.increase_latency(target=-1, epochs=2)

    with pytest.raises(ValueError):
        policies.degradation.increase_latency(target=20)

    graph = build_graph()
    policy = policies.degradation.increase_latency(rate=0.5, epochs=2)
    policy(graph)
    policy(graph)

    assert graph.edges["a", "b"]["latency"] == 22


def test_degrade_combines_capacity_and_latency_changes():
    graph = build_graph()

    policy = policies.degradation.degrade(
        0.25,
        2,
        node_assets="cpu",
        edge_assets=["bandwidth", "latency"],
    )

    policy(graph)
    policy(graph)

    assert graph.nodes["a"]["cpu"] == 20
    assert graph.edges["a", "b"]["bandwidth"] == 25
    assert graph.edges["a", "b"]["latency"] == 40
