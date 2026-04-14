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
