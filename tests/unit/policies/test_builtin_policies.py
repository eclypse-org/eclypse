from __future__ import annotations

import sys
from types import SimpleNamespace
from typing import Any

import pytest

from eclypse.graph.asset_graph import AssetGraph
from eclypse.graph.assets import Additive
from eclypse.policies import (
    after,
    availability_flap,
    between,
    bounded_random_walk,
    degrade,
    every,
    from_dataframe,
    from_parquet,
    from_records,
    increase_latency,
    jitter_bandwidth,
    jitter_latency,
    jitter_resources,
    kill_nodes,
    latency_spike,
    normalize_update_policies,
    once_at,
    reduce_capacity,
    replay_edges,
    replay_nodes,
    revive_nodes,
)
from eclypse.policies._filters import (
    clamp,
    coerce_numeric_like,
    ensure_numeric_value,
    iter_selected_edges,
    iter_selected_keys,
    iter_selected_nodes,
)


class FakeDataFrame:
    def __init__(self, records):
        self._records = records

    def to_dict(self, orient: str):
        assert orient == "records"
        return self._records


class IterRowsFrame:
    def __init__(self, records):
        self._records = records

    def iterrows(self):
        yield from enumerate(self._records)


def build_graph(seed: int = 7) -> AssetGraph:
    graph = AssetGraph(
        "dynamic",
        seed=seed,
        node_assets={
            "cpu": Additive(0, 1000),
            "ram": Additive(0, 1000),
            "availability": Additive(0, 1),
        },
        edge_assets={
            "latency": Additive(0, 10_000),
            "bandwidth": Additive(0, 10_000),
        },
    )
    graph.add_node("a", cpu=80, ram=32, availability=1.0)
    graph.add_node("b", cpu=50, ram=16, availability=1.0)
    graph.add_edge("a", "b", latency=10, bandwidth=100)
    return graph


def test_failure_policies_target_selected_nodes_and_edges():
    graph = build_graph()

    kill_nodes(1.0, node_ids=["a"])(graph)
    assert graph.nodes["a"]["availability"] == 0.0
    assert graph.nodes["b"]["availability"] == 1.0

    revive_nodes(1.0, node_ids=["a"])(graph)
    assert graph.nodes["a"]["availability"] == 0.99

    availability_flap(1.0, node_ids=["b"])(graph)
    assert graph.nodes["b"]["availability"] == 0.0

    latency_spike(1.0, min_increase=5.0, max_increase=5.0, edge_ids=[("a", "b")])(graph)
    assert graph.edges["a", "b"]["latency"] == 15


def test_normalize_update_policies_and_filter_helpers_cover_edge_cases():
    def policy(_graph):
        return None

    assert normalize_update_policies(None) == []
    assert normalize_update_policies(policy) == [policy]
    assert normalize_update_policies([policy]) == [policy]

    graph = build_graph()

    assert iter_selected_nodes(
        graph, node_filter=lambda node_id, _: node_id == "a"
    ) == [("a", graph.nodes["a"])]
    assert iter_selected_edges(
        graph,
        edge_filter=lambda source, target, _: (source, target) == ("a", "b"),
    ) == [("a", "b", graph.edges["a", "b"])]
    assert iter_selected_keys(graph.nodes["a"], ["cpu", "missing"]) == ["cpu"]

    with pytest.raises(TypeError):
        ensure_numeric_value("availability", True)

    with pytest.raises(TypeError):
        ensure_numeric_value("cpu", "busy")

    assert clamp(5, upper=3) == 3
    assert coerce_numeric_like(True, 1.5) == 1.5


def test_noise_policies_change_only_selected_resources():
    graph = build_graph()

    jitter_resources(
        node_assets="cpu",
        edge_assets="bandwidth",
        node_range=(1.5, 1.5),
        edge_range=(0.5, 0.5),
    )(graph)

    assert graph.nodes["a"]["cpu"] == 120
    assert graph.nodes["a"]["ram"] == 32
    assert graph.edges["a", "b"]["bandwidth"] == 50
    assert graph.edges["a", "b"]["latency"] == 10

    jitter_latency(relative_range=(2.0, 2.0))(graph)
    jitter_bandwidth(relative_range=(0.5, 0.5))(graph)

    assert graph.edges["a", "b"]["latency"] == 20
    assert graph.edges["a", "b"]["bandwidth"] == 25


def test_noise_policy_validation_and_derived_asset_selection():
    with pytest.raises(ValueError):
        jitter_resources(node_range=(2.0, 1.0))

    with pytest.raises(ValueError):
        jitter_resources(edge_range=(2.0, 1.0))

    with pytest.raises(ValueError):
        bounded_random_walk()

    with pytest.raises(ValueError):
        bounded_random_walk(node_steps={"cpu": -1})

    with pytest.raises(ValueError):
        bounded_random_walk(edge_steps={"latency": -1})

    graph = build_graph()
    jitter_resources(
        node_ranges={"cpu": (0.5, 0.5)},
        edge_ranges={"latency": (2.0, 2.0)},
    )(graph)

    assert graph.nodes["a"]["cpu"] == 40
    assert graph.nodes["a"]["ram"] == 32
    assert graph.edges["a", "b"]["latency"] == 20
    assert graph.edges["a", "b"]["bandwidth"] == 100


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


def test_degradation_policies_stop_at_the_requested_epoch():
    graph = build_graph()

    reduce = reduce_capacity(
        0.25,
        2,
        node_assets="cpu",
        edge_assets="bandwidth",
    )
    latency = increase_latency(target=40, epochs=2)

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
        reduce_capacity(0.5, 0)

    with pytest.raises(ValueError):
        degrade(0.0, 2)

    with pytest.raises(ValueError):
        increase_latency()

    with pytest.raises(ValueError):
        increase_latency(rate=0.1, target=20, epochs=2)

    with pytest.raises(ValueError):
        increase_latency(rate=-2.0)

    with pytest.raises(ValueError):
        increase_latency(target=-1, epochs=2)

    with pytest.raises(ValueError):
        increase_latency(target=20)

    graph = build_graph()
    policy = increase_latency(rate=0.5, epochs=2)
    policy(graph)
    policy(graph)

    assert graph.edges["a", "b"]["latency"] == 22


def test_degrade_combines_capacity_and_latency_changes():
    graph = build_graph()

    policy = degrade(
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


def test_trace_driven_policies_replay_node_and_edge_records():
    graph = build_graph()

    node_policy = replay_nodes(
        [
            {"time": 0, "node": "a", "cpu": 70},
            {"time": 1, "node": "a", "cpu": 55},
        ],
        time_column="time",
        node_id_column="node",
    )

    edge_policy = replay_edges(
        [
            {"time": 0, "src": "a", "dst": "b", "latency": 12},
            {"time": 1, "src": "a", "dst": "b", "latency": 18},
        ],
        time_column="time",
        source_column="src",
        target_column="dst",
    )

    node_policy(graph)
    edge_policy(graph)
    assert graph.nodes["a"]["cpu"] == 70
    assert graph.edges["a", "b"]["latency"] == 12

    node_policy(graph)
    edge_policy(graph)
    assert graph.nodes["a"]["cpu"] == 55
    assert graph.edges["a", "b"]["latency"] == 18


def test_trace_driven_convenience_builders_accept_records_and_dataframe_like():
    graph = build_graph()

    from_records(
        [
            {"step": 0, "node_id": "a", "ram": 64},
        ],
        target="nodes",
        time_column="step",
    )(graph)

    assert graph.nodes["a"]["ram"] == 64

    from_dataframe(
        FakeDataFrame(
            [
                {"step": 0, "source": "a", "target": "b", "bandwidth": 250},
            ]
        ),
        target="edges",
        time_column="step",
    )(graph)

    assert graph.edges["a", "b"]["bandwidth"] == 250


def test_trace_driven_builders_cover_invalid_targets_and_parquet_loading(
    monkeypatch: pytest.MonkeyPatch,
):
    graph = build_graph()
    invalid_target: Any = "services"

    with pytest.raises(ValueError):
        from_records([], target=invalid_target)

    from_dataframe(
        IterRowsFrame([{"step": 0, "node_id": "a", "cpu": 44}]),
        target="nodes",
        time_column="step",
    )(graph)

    assert graph.nodes["a"]["cpu"] == 44

    fake_pandas = SimpleNamespace(
        read_parquet=lambda path: FakeDataFrame(
            [{"step": 0, "node_id": "a", "ram": 99}]
        )
    )
    monkeypatch.setitem(sys.modules, "pandas", fake_pandas)

    from_parquet(
        "trace.parquet",
        target="nodes",
        time_column="step",
    )(graph)

    assert graph.nodes["a"]["ram"] == 99


def test_schedule_wrappers_control_policy_timing():
    graph = AssetGraph(
        "scheduled",
        node_assets={"cpu": Additive(0, 100)},
        update_policies=[
            every(
                2,
                lambda graph: graph.nodes["a"].update(cpu=graph.nodes["a"]["cpu"] + 1),
            ),
            after(
                1,
                lambda graph: graph.nodes["a"].update(cpu=graph.nodes["a"]["cpu"] + 1),
            ),
            between(
                1,
                2,
                lambda graph: graph.nodes["a"].update(cpu=graph.nodes["a"]["cpu"] + 1),
            ),
            once_at(
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
        after(-1, noop)

    with pytest.raises(ValueError):
        between(-1, 1, noop)

    with pytest.raises(ValueError):
        between(3, 2, noop)

    with pytest.raises(ValueError):
        every(0, noop)

    with pytest.raises(ValueError):
        every(1, noop, start=-1)

    with pytest.raises(ValueError):
        once_at(-1, noop)


def test_trace_driven_missing_error_is_explicit():
    graph = build_graph()
    policy = replay_nodes(
        [{"time": 0, "node_id": "missing", "cpu": 1}],
        missing="error",
    )

    with pytest.raises(KeyError):
        policy(graph)


def test_trace_driven_filters_start_step_and_edge_missing_behaviour():
    graph = build_graph()

    node_policy = replay_nodes(
        [
            {"time": 4, "node_id": "a", "cpu": 33},
            {"time": 5, "node_id": "b", "cpu": 22},
        ],
        start_step=4,
        node_ids=["a"],
        node_filter=lambda node_id, _: node_id == "a",
    )

    edge_policy = replay_edges(
        [{"time": 0, "source": "a", "target": "missing", "latency": 1}],
        missing="ignore",
    )

    node_policy(graph)
    edge_policy(graph)
    assert graph.nodes["a"]["cpu"] == 33
    assert graph.nodes["b"]["cpu"] == 50

    node_policy(graph)
    assert graph.nodes["b"]["cpu"] == 50

    failing_edge_policy = replay_edges(
        [{"time": 0, "source": "a", "target": "missing", "latency": 1}],
        missing="error",
    )

    with pytest.raises(KeyError):
        failing_edge_policy(graph)


def test_failure_policy_validation_and_alternative_branches():
    with pytest.raises(ValueError):
        kill_nodes(1.5)

    with pytest.raises(ValueError):
        availability_flap(-0.1)

    with pytest.raises(ValueError):
        latency_spike(1.0, factor=-1)

    with pytest.raises(ValueError):
        latency_spike(1.0, min_increase=-1)

    with pytest.raises(ValueError):
        latency_spike(1.0, min_increase=2, max_increase=1)

    graph = build_graph()
    graph.nodes["a"]["availability"] = 0.0

    availability_flap(
        0.0,
        up_probability=1.0,
        up_availability=0.75,
        node_ids=["a"],
        unavailable_at_or_below=0.0,
    )(graph)
    assert graph.nodes["a"]["availability"] == 0.75

    latency_spike(1.0, factor=2.0)(graph)
    assert graph.edges["a", "b"]["latency"] == 20
