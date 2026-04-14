from __future__ import annotations

import pytest

from eclypse.policies import bounded_random_walk
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
