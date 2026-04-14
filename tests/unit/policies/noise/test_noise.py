from __future__ import annotations

import pytest

from eclypse.policies import (
    bounded_random_walk,
    impulse,
    momentum_walk,
)
from tests.unit.policies._helpers import build_graph


def test_bounded_random_walk_stays_within_bounds():
    graph = build_graph()

    policy = bounded_random_walk(
        node_steps={"cpu": 25},
        edge_steps={"latency": 5},
        node_bounds={"cpu": (0, 90)},
        edge_bounds={"latency": (0, 12)},
    )

    for _ in range(20):
        policy(graph)
        assert 0 <= graph.nodes["a"]["cpu"] <= 90
        assert 0 <= graph.edges["a", "b"]["latency"] <= 12


def test_bounded_random_walk_validation():
    with pytest.raises(ValueError):
        bounded_random_walk()

    with pytest.raises(ValueError):
        bounded_random_walk(node_steps={"cpu": -1})

    with pytest.raises(ValueError):
        bounded_random_walk(edge_steps={"latency": -1})


def test_momentum_walk_stays_within_bounds():
    graph = build_graph()

    policy = momentum_walk(
        node_steps={"cpu": 25},
        edge_steps={"latency": 5},
        node_bounds={"cpu": (0, 90)},
        edge_bounds={"latency": (0, 12)},
        momentum=0.8,
    )

    for _ in range(20):
        policy(graph)
        assert 0 <= graph.nodes["a"]["cpu"] <= 90
        assert 0 <= graph.edges["a", "b"]["latency"] <= 12


def test_momentum_walk_uses_graph_rng_reproducibly():
    first_graph = build_graph()
    second_graph = build_graph()

    first_policy = momentum_walk(
        node_steps={"cpu": 10},
        edge_steps={"latency": 2},
        momentum=0.6,
    )
    second_policy = momentum_walk(
        node_steps={"cpu": 10},
        edge_steps={"latency": 2},
        momentum=0.6,
    )

    for _ in range(5):
        first_policy(first_graph)
        second_policy(second_graph)

    assert first_graph.nodes["a"]["cpu"] == second_graph.nodes["a"]["cpu"]
    assert (
        first_graph.edges["a", "b"]["latency"]
        == second_graph.edges["a", "b"]["latency"]
    )


def test_momentum_walk_validation():
    with pytest.raises(ValueError):
        momentum_walk()

    with pytest.raises(ValueError):
        momentum_walk(node_steps={"cpu": -1})

    with pytest.raises(ValueError):
        momentum_walk(momentum=1.5, node_steps={"cpu": 1})


def test_impulse_applies_selected_shocks():
    graph = build_graph()

    impulse(
        node_assets="cpu",
        edge_assets="bandwidth",
        probability=1.0,
        node_factor_range=(1.5, 1.5),
        edge_factor_range=(0.5, 0.5),
    )(graph)

    assert graph.nodes["a"]["cpu"] == 120
    assert graph.nodes["a"]["ram"] == 32
    assert graph.edges["a", "b"]["bandwidth"] == 50
    assert graph.edges["a", "b"]["latency"] == 10


def test_impulse_can_skip_updates():
    graph = build_graph()

    impulse(
        node_assets="cpu",
        edge_assets="bandwidth",
        probability=0.0,
    )(graph)

    assert graph.nodes["a"]["cpu"] == 80
    assert graph.edges["a", "b"]["bandwidth"] == 100


def test_impulse_validation():
    with pytest.raises(ValueError):
        impulse()

    with pytest.raises(ValueError):
        impulse(node_assets="cpu", probability=-0.1)

    with pytest.raises(ValueError):
        impulse(node_assets="cpu", node_factor_range=(-1.0, 1.0))

    with pytest.raises(ValueError):
        impulse(node_assets="cpu", node_factor_range=(2.0, 1.0))
