from __future__ import annotations

import pytest

from eclypse.policies import normalize_update_policies
from eclypse.policies._filters import (
    clamp,
    coerce_numeric_like,
    ensure_numeric_value,
    iter_selected_edges,
    iter_selected_keys,
    iter_selected_nodes,
)
from tests.unit.policies._helpers import build_graph


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
