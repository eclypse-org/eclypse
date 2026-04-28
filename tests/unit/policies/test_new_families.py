from __future__ import annotations

import pytest

from eclypse import policies
from tests.unit.policies._helpers import build_graph


def test_compose_family_combines_policies():
    graph = build_graph()

    def add_cpu(target_graph):
        target_graph.nodes["a"].update(cpu=81)

    def add_ram(target_graph):
        target_graph.nodes["a"].update(ram=33)

    policies.compose.chain(add_cpu, add_ram)(graph)
    assert graph.nodes["a"]["cpu"] == 81
    assert graph.nodes["a"]["ram"] == 33

    policies.compose.conditional(lambda _: True, add_cpu)(graph)
    assert graph.nodes["a"]["cpu"] == 81

    policies.compose.one_of(add_cpu)(graph)
    policies.compose.weighted_choice([add_ram], [1.0])(graph)
    assert graph.nodes["a"]["ram"] == 33

    with pytest.raises(ValueError):
        policies.compose.one_of()
    with pytest.raises(ValueError):
        policies.compose.weighted_choice([add_cpu], [0.0])


def test_workload_family_updates_load_values():
    graph = build_graph()
    graph.nodes["a"]["users"] = 0
    graph.edges["a", "b"]["traffic"] = 0

    policies.workload.arrival_process(2, node_assets="users")(graph)
    assert graph.nodes["a"]["users"] >= 0

    policies.workload.traffic_matrix({("a", "b"): 12})(graph)
    assert graph.edges["a", "b"]["traffic"] == 12

    policy = policies.workload.diurnal_load(
        amplitude=1,
        period=4,
        node_assets="cpu",
    )
    policy(graph)
    policy(graph)
    assert graph.nodes["a"]["cpu"] >= 80

    with pytest.raises(ValueError):
        policies.workload.arrival_process(-1, node_assets="users")


def test_topology_family_mutates_graph_structure():
    graph = build_graph()

    policies.topology.add_node("c", cpu=1, ram=1, availability=1.0)(graph)
    assert graph.has_node("c")

    policies.topology.add_edge("b", "c", latency=1, bandwidth=1)(graph)
    assert graph.has_edge("b", "c")

    policies.topology.rewire([("a", "b")], probability=1.0)(graph)
    assert not graph.has_edge("a", "b")

    policies.topology.churn(
        add_probability=1.0,
        candidate_nodes={"d": {"cpu": 1, "ram": 1, "availability": 1.0}},
    )(graph)
    assert graph.has_node("d")

    policies.topology.remove_node("d")(graph)
    assert not graph.has_node("d")


def test_constraints_family_enforces_numeric_invariants():
    graph = build_graph()

    policies.constraints.clamp_values(upper=60, node_assets="cpu")(graph)
    assert graph.nodes["a"]["cpu"] == 60

    policies.constraints.round_int(node_assets="availability")(graph)
    assert graph.nodes["a"]["availability"] == 1

    policies.constraints.ensure_capacity_floor(70, edge_assets="bandwidth")(graph)
    assert graph.edges["a", "b"]["bandwidth"] == 100

    policies.constraints.normalise(100, node_assets="cpu")(graph)
    assert graph.nodes["a"]["cpu"] + graph.nodes["b"]["cpu"] == 100
