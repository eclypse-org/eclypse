from __future__ import annotations

import pytest

from eclypse import policies
from eclypse.policies.degrade._helpers import _build_value_adjustment_policy
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

    reduce(graph)
    increase(graph)
    assert graph.nodes["a"]["cpu"] == 20
    assert graph.edges["a", "b"]["latency"] == 40


def test_degrade_validation_and_factor_mode():
    with pytest.raises(ValueError):
        policies.degrade.reduce(factor=0.5, epochs=0)

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


def test_overrides_support_per_asset_overrides():
    graph = build_graph()

    policy = policies.degrade.reduce(
        factor=0.5,
        epochs=2,
        node_assets="cpu",
        edge_asset_overrides={
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


def test_reduce_and_increase_target_direction_validation():
    graph = build_graph()

    with pytest.raises(ValueError):
        policies.degrade.increase(target=5, epochs=2, edge_assets="latency")(graph)

    with pytest.raises(ValueError):
        policies.degrade.reduce(target=20, epochs=2, edge_assets="latency")(graph)


def test_increase_and_reduce_can_be_composed_explicitly():
    graph = build_graph()

    reduce_policy = policies.degrade.reduce(
        factor=0.5,
        epochs=2,
        node_assets="cpu",
        edge_asset_overrides={
            "bandwidth": {
                "factor": 0.25,
                "epochs": 2,
            }
        },
    )
    increase_policy = policies.degrade.increase(
        factor=2.0,
        epochs=2,
        edge_assets="latency",
        node_asset_overrides={
            "ram": {
                "target": 64,
                "epochs": 2,
            }
        },
    )

    for _ in range(2):
        reduce_policy(graph)
        increase_policy(graph)

    assert graph.nodes["a"]["cpu"] == 40
    assert graph.nodes["a"]["ram"] == 64
    assert graph.edges["a", "b"]["bandwidth"] == 25
    assert graph.edges["a", "b"]["latency"] == 20


def test_additional_degrade_policies_transform_values():
    graph = build_graph()

    policies.degrade.set_value(
        10,
        node_assets="cpu",
        edge_values={"bandwidth": 40},
    )(graph)
    assert graph.nodes["a"]["cpu"] == 10
    assert graph.edges["a", "b"]["bandwidth"] == 40

    policies.degrade.scale(2, node_assets="cpu")(graph)
    assert graph.nodes["a"]["cpu"] == 20

    policies.degrade.scale(0.5, edge_assets="bandwidth")(graph)
    assert graph.edges["a", "b"]["bandwidth"] == 20

    policies.constraints.clamp_values(upper=15, node_assets="cpu")(graph)
    assert graph.nodes["a"]["cpu"] == 15

    ramp = policies.degrade.ramp_to(60, epochs=2, node_assets="cpu")
    ramp(graph)
    ramp(graph)
    assert graph.nodes["a"]["cpu"] == 60


def test_additional_degrade_policies_validate_inputs():
    with pytest.raises(ValueError):
        policies.degrade.scale(1.0)
    with pytest.raises(ValueError):
        policies.constraints.clamp_values(lower=2, upper=1, node_assets="cpu")
    with pytest.raises(ValueError):
        policies.degrade.ramp_to(1, epochs=0, node_assets="cpu")
    with pytest.raises(ValueError, match="At least one"):
        policies.degrade.ramp_to(1, epochs=2)


def test_ramp_supports_edge_targets_and_stops_after_completion():
    graph = build_graph()
    ramp = policies.degrade.ramp_to(
        0,
        epochs=2,
        edge_assets=["latency", "bandwidth"],
        edge_targets={"bandwidth": 25},
    )
    ramp(graph)
    assert graph.edges["a", "b"]["latency"] == 5
    assert graph.edges["a", "b"]["bandwidth"] == 50
    ramp(graph)
    ramp(graph)
    assert graph.edges["a", "b"]["latency"] == 0
    assert graph.edges["a", "b"]["bandwidth"] == 25


def test_degrade_basis_initial_uses_first_seen_value():
    graph = build_graph()

    policy = policies.degrade.scale(0.5, node_assets="cpu", basis="initial")
    policy(graph)
    assert graph.nodes["a"]["cpu"] == 40

    graph.nodes["a"]["cpu"] = 200
    policy(graph)
    assert graph.nodes["a"]["cpu"] == 40

    reduce_policy = policies.degrade.reduce(
        factor=0.25,
        epochs=2,
        node_assets="cpu",
        basis="initial",
    )
    graph.nodes["a"]["cpu"] = 80
    reduce_policy(graph)
    graph.nodes["a"]["cpu"] = 1000
    reduce_policy(graph)
    assert graph.nodes["a"]["cpu"] == 20


@pytest.mark.parametrize(
    ("factory", "kwargs", "message"),
    [
        (policies.degrade.reduce, {"factor": 0.5}, "epochs must be provided"),
        (policies.degrade.reduce, {"factor": 0.5, "epochs": 0}, "strictly positive"),
        (policies.degrade.reduce, {"epochs": 2}, "Exactly one"),
        (policies.degrade.increase, {"factor": 0.5, "epochs": 2}, "greater than"),
        (policies.degrade.reduce, {"factor": 2, "epochs": 2}, "between 0 and 1"),
        (policies.degrade.increase, {"target": -1, "epochs": 2}, "non-negative"),
    ],
)
def test_degrade_validates_adjustment_with_selected_assets(factory, kwargs, message):
    with pytest.raises(ValueError, match=message):
        factory(node_assets="cpu", **kwargs)


def test_adjustment_builder_rejects_missing_assets_and_invalid_direction():
    with pytest.raises(ValueError, match="At least one"):
        _build_value_adjustment_policy("reduce", factor=0.5, epochs=2)
    with pytest.raises(ValueError, match="direction must"):
        _build_value_adjustment_policy("invalid", factor=1, epochs=2, node_assets="cpu")
    with pytest.raises(ValueError, match="unsupported fields: unknown"):
        policies.degrade.reduce(
            node_asset_overrides={"cpu": {"factor": 0.5, "epochs": 2, "unknown": 1}}
        )


def test_set_value_uses_node_overrides_and_default_for_other_assets():
    graph = build_graph()
    policies.degrade.set_value(10, node_assets=["cpu", "ram"], node_values={"cpu": 5})(
        graph
    )
    assert graph.nodes["a"]["cpu"] == 5
    assert graph.nodes["a"]["ram"] == 10
