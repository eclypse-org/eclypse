from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    cast,
)

import pytest

from eclypse import policies
from tests.unit.policies._helpers import build_graph

if TYPE_CHECKING:
    from eclypse.utils.types import ReplayTarget


class FakeDataFrame:
    def __init__(self, records):
        self._records = records

    def to_dict(self, orient: str):
        assert orient == "records"
        return self._records


def test_replay_policies_replay_node_and_edge_records():
    graph = build_graph()

    node_policy = policies.replay.replay_nodes(
        [
            {"time": 0, "node_id": "a", "cpu": 4},
            {"time": 1, "node_id": "a", "cpu": 6},
        ],
        value_columns=["cpu"],
    )
    edge_policy = policies.replay.replay_edges(
        [
            {"time": 0, "source": "a", "target": "b", "latency": 14},
            {"time": 1, "source": "a", "target": "b", "latency": 20},
        ],
        value_columns=["latency"],
    )

    node_policy(graph)
    edge_policy(graph)
    assert graph.nodes["a"]["cpu"] == 4
    assert graph.edges["a", "b"]["latency"] == 14

    node_policy(graph)
    edge_policy(graph)
    assert graph.nodes["a"]["cpu"] == 6
    assert graph.edges["a", "b"]["latency"] == 20


def test_replay_convenience_builders_accept_records_and_dataframe_like():
    graph = build_graph()

    policies.replay.from_records(
        [
            {"time": 0, "node_id": "a", "cpu": 7},
            {"time": 1, "node_id": "a", "cpu": 9},
        ],
        target="nodes",
        value_columns=["cpu"],
    )(graph)

    assert graph.nodes["a"]["cpu"] == 7

    policies.replay.from_dataframe(
        FakeDataFrame(
            [
                {"time": 0, "source": "a", "target": "b", "bandwidth": 80},
                {"time": 1, "source": "a", "target": "b", "bandwidth": 60},
            ]
        ),
        target="edges",
        value_columns=["bandwidth"],
    )(graph)

    assert graph.edges["a", "b"]["bandwidth"] == 80


def test_replay_builders_cover_invalid_targets_and_parquet_loading(
    monkeypatch,
):
    invalid_target = cast("ReplayTarget", "services")
    with pytest.raises(ValueError):
        policies.replay.from_records([], target=invalid_target)

    policies.replay.from_dataframe(
        FakeDataFrame([]),
        target="nodes",
    )

    class FakePandas:
        @staticmethod
        def read_parquet(path):
            assert path == "trace.parquet"
            return FakeDataFrame(
                [
                    {"time": 0, "node_id": "a", "cpu": 3},
                ]
            )

    monkeypatch.setitem(__import__("sys").modules, "pandas", FakePandas)
    graph = build_graph()
    policies.replay.from_parquet(
        "trace.parquet",
        target="nodes",
        value_columns=["cpu"],
    )(graph)
    assert graph.nodes["a"]["cpu"] == 3


def test_replay_missing_error_is_explicit():
    graph = build_graph()
    policy = policies.replay.replay_nodes(
        [{"time": 0, "node_id": "missing", "cpu": 10}],
        value_columns=["cpu"],
        missing="error",
    )

    with pytest.raises(KeyError):
        policy(graph)


def test_replay_filters_start_step_and_edge_missing_behaviour():
    graph = build_graph()

    node_policy = policies.replay.replay_nodes(
        [
            {"time": 3, "node_id": "a", "cpu": 11},
            {"time": 4, "node_id": "a", "cpu": 13},
        ],
        node_filter=lambda node_id, _: node_id == "a",
        start_step=3,
        value_columns=["cpu"],
    )
    node_policy(graph)
    assert graph.nodes["a"]["cpu"] == 11

    edge_policy = policies.replay.replay_edges(
        [
            {"time": 1, "source": "a", "target": "b", "bandwidth": 77},
            {"time": 2, "source": "b", "target": "c", "bandwidth": 55},
        ],
        edge_ids=[("a", "b")],
        start_step=1,
        value_columns=["bandwidth"],
    )
    edge_policy(graph)
    assert graph.edges["a", "b"]["bandwidth"] == 77

    failing_edge_policy = policies.replay.replay_edges(
        [{"time": 0, "source": "x", "target": "y", "bandwidth": 10}],
        value_columns=["bandwidth"],
        missing="error",
    )
    with pytest.raises(KeyError):
        failing_edge_policy(graph)
