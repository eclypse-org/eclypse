from __future__ import annotations

import pytest

from eclypse import policies
from eclypse.graph.asset_graph import AssetGraph
from eclypse.graph.assets import Additive


def test_schedule_wrappers_control_policy_timing():
    graph = AssetGraph(
        "scheduled",
        node_assets={"cpu": Additive(0, 100)},
        update_policies=[
            policies.every(
                2,
                lambda graph: graph.nodes["a"].update(cpu=graph.nodes["a"]["cpu"] + 1),
            ),
            policies.after(
                1,
                lambda graph: graph.nodes["a"].update(cpu=graph.nodes["a"]["cpu"] + 1),
            ),
            policies.between(
                1,
                2,
                lambda graph: graph.nodes["a"].update(cpu=graph.nodes["a"]["cpu"] + 1),
            ),
            policies.once_at(
                2,
                lambda graph: graph.nodes["a"].update(cpu=graph.nodes["a"]["cpu"] + 1),
            ),
        ],
    )
    graph.add_node("a", cpu=0)

    for _ in range(4):
        graph.evolve()

    assert graph.nodes["a"]["cpu"] == 8


def test_schedule_wrapper_validation_errors():
    def noop(_graph):
        return None

    with pytest.raises(ValueError):
        policies.after(-1, noop)

    with pytest.raises(ValueError):
        policies.between(-1, 1, noop)

    with pytest.raises(ValueError):
        policies.between(3, 2, noop)

    with pytest.raises(ValueError):
        policies.every(0, noop)

    with pytest.raises(ValueError):
        policies.every(1, noop, start=-1)

    with pytest.raises(ValueError):
        policies.once_at(-1, noop)

    with pytest.raises(ValueError):
        policies.at([], noop)
    with pytest.raises(ValueError):
        policies.at([-1], noop)

    with pytest.raises(ValueError):
        policies.until(-1, noop)

    with pytest.raises(ValueError):
        policies.repeat(-1, noop)

    with pytest.raises(ValueError):
        policies.with_probability(1.5, noop)

    with pytest.raises(ValueError):
        policies.jittered_every(0, noop)
    with pytest.raises(ValueError):
        policies.jittered_every(1, noop, jitter=-1)
    with pytest.raises(ValueError):
        policies.jittered_every(1, noop, start=-1)

    with pytest.raises(ValueError):
        policies.cooldown(-1, noop)


def test_additional_schedule_wrappers_control_policy_timing():
    graph = AssetGraph("scheduled", node_assets={"cpu": Additive(0, 100)})
    graph.add_node("a", cpu=0)

    def increment(target_graph):
        target_graph.nodes["a"]["cpu"] += 1

    wrappers = [
        policies.at([1, 3], increment),
        policies.until(1, increment),
        policies.repeat(2, increment),
        policies.with_probability(1.0, increment),
        policies.jittered_every(2, increment, jitter=0),
        policies.cooldown(1, increment),
    ]

    for _ in range(4):
        for wrapper in wrappers:
            wrapper(graph)

    assert graph.nodes["a"]["cpu"] == 14
