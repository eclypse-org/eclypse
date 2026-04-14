from __future__ import annotations

import pytest

from eclypse import policies
from tests.unit.policies._helpers import build_graph


def test_degrade_policies_stop_at_the_requested_epoch():
    graph = build_graph()

    reduce = policies.degrade.reduce(
        factor=0.25,
        epochs=2,
        node_assets="cpu",
        edge_assets="bandwidth",
    )
    increase = policies.degrade.increase(
        target=40,
        epochs=2,
        edge_assets="latency",
    )

    reduce(graph)
    increase(graph)
    assert graph.nodes["a"]["cpu"] == 40
    assert graph.edges["a", "b"]["bandwidth"] == 50
    assert graph.edges["a", "b"]["latency"] == 20

    reduce(graph)
    increase(graph)
    assert graph.nodes["a"]["cpu"] == 20
    assert graph.edges["a", "b"]["bandwidth"] == 25
    assert graph.edges["a", "b"]["latency"] == 40


def test_degrade_validation_and_factor_mode():
    with pytest.raises(ValueError):
        policies.degrade.reduce(factor=0.5, epochs=0)

    with pytest.raises(ValueError):
        policies.degrade.degrade()

    with pytest.raises(ValueError):
        policies.degrade.increase(epochs=2)

    with pytest.raises(ValueError):
        policies.degrade.increase(factor=1.1, target=20, epochs=2)

    with pytest.raises(ValueError):
        policies.degrade.increase(factor=0.5, epochs=2)

    with pytest.raises(ValueError):
        policies.degrade.increase(target=-1, epochs=2)

    with pytest.raises(ValueError):
        policies.degrade.reduce(factor=0.5, epochs=2)

    with pytest.raises(ValueError):
        policies.degrade.increase(factor=2.0, epochs=2)

    graph = build_graph()
    policy = policies.degrade.increase(
        factor=2.25,
        epochs=2,
        edge_assets="latency",
    )
    policy(graph)
    policy(graph)

    assert graph.edges["a", "b"]["latency"] == 22


def test_adjustments_support_per_asset_overrides():
    graph = build_graph()

    policy = policies.degrade.reduce(
        factor=0.5,
        epochs=2,
        node_assets="cpu",
        edge_asset_adjustments={
            "bandwidth": {
                "factor": 0.25,
                "epochs": 2,
            }
        },
    )

    policy(graph)
    policy(graph)

    assert graph.nodes["a"]["cpu"] == 40
    assert graph.edges["a", "b"]["bandwidth"] == 25


def test_degrade_combines_increase_and_reduce_changes():
    graph = build_graph()

    policy = policies.degrade.degrade(
        reduce_factor=0.25,
        reduce_epochs=2,
        increase_factor=4.0,
        increase_epochs=2,
        reduce_node_assets="cpu",
        reduce_edge_assets="bandwidth",
        increase_edge_assets="latency",
    )

    policy(graph)
    policy(graph)

    assert graph.nodes["a"]["cpu"] == 20
    assert graph.edges["a", "b"]["bandwidth"] == 25
    assert graph.edges["a", "b"]["latency"] == 40


def test_reduce_and_increase_target_direction_validation():
    graph = build_graph()

    with pytest.raises(ValueError):
        policies.degrade.increase(target=5, epochs=2, edge_assets="latency")(graph)

    with pytest.raises(ValueError):
        policies.degrade.reduce(target=20, epochs=2, edge_assets="latency")(graph)


def test_degrade_supports_per_asset_overrides_for_each_phase():
    graph = build_graph()

    policy = policies.degrade.degrade(
        reduce_factor=0.5,
        reduce_epochs=2,
        increase_factor=2.0,
        increase_epochs=2,
        reduce_node_assets="cpu",
        increase_edge_assets="latency",
        reduce_edge_asset_adjustments={
            "bandwidth": {
                "factor": 0.25,
                "epochs": 2,
            }
        },
        increase_node_asset_adjustments={
            "ram": {
                "target": 64,
                "epochs": 2,
            }
        },
    )

    policy(graph)
    policy(graph)

    assert graph.nodes["a"]["cpu"] == 40
    assert graph.nodes["a"]["ram"] == 64
    assert graph.edges["a", "b"]["bandwidth"] == 25
    assert graph.edges["a", "b"]["latency"] == 20
