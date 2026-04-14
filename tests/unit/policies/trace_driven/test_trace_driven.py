from __future__ import annotations

import sys
from types import SimpleNamespace
from typing import Any

import pytest

from eclypse.policies import (
    from_dataframe,
    from_parquet,
    from_records,
    replay_edges,
    replay_nodes,
)
from tests.unit.policies._helpers import (
    FakeDataFrame,
    IterRowsFrame,
    build_graph,
)


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
