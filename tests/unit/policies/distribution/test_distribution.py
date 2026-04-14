from __future__ import annotations

import math

import pytest

from eclypse.policies import (
    beta,
    categorical,
    gamma,
    lognormal,
    normal,
    triangular,
    truncated_normal,
    uniform,
)
from tests.unit.policies._helpers import build_graph


def test_uniform_distribution_policy_changes_only_selected_resources():
    graph = build_graph()

    uniform(
        node_assets="cpu",
        edge_assets="bandwidth",
        node_distribution=(1.5, 1.5),
        edge_distribution=(0.5, 0.5),
    )(graph)

    assert graph.nodes["a"]["cpu"] == 120
    assert graph.nodes["a"]["ram"] == 32
    assert graph.edges["a", "b"]["bandwidth"] == 50
    assert graph.edges["a", "b"]["latency"] == 10


def test_uniform_distribution_validation_and_derived_asset_selection():
    with pytest.raises(ValueError):
        uniform(node_distribution=(2.0, 1.0))

    with pytest.raises(ValueError):
        uniform(edge_distribution=(2.0, 1.0))

    with pytest.raises(ValueError):
        uniform()

    graph = build_graph()
    uniform(
        node_asset_distributions={"cpu": (0.5, 0.5)},
        edge_asset_distributions={"latency": (2.0, 2.0)},
    )(graph)

    assert graph.nodes["a"]["cpu"] == 40
    assert graph.nodes["a"]["ram"] == 32
    assert graph.edges["a", "b"]["latency"] == 20
    assert graph.edges["a", "b"]["bandwidth"] == 100


def test_uniform_distribution_uses_union_of_assets_and_per_asset_overrides():
    graph = build_graph()
    graph.nodes["a"]["storage"] = 40

    uniform(
        node_assets=["cpu", "ram"],
        node_distribution=(2.0, 2.0),
        node_asset_distributions={"cpu": (0.5, 0.5), "storage": (3.0, 3.0)},
    )(graph)

    assert graph.nodes["a"]["cpu"] == 40
    assert graph.nodes["a"]["ram"] == 64
    assert graph.nodes["a"]["storage"] == 120


def test_uniform_distribution_uses_graph_rng_reproducibly():
    first_graph = build_graph()
    second_graph = build_graph()

    first_policy = uniform(
        node_assets="cpu",
        edge_assets="latency",
        node_distribution=(0.8, 1.2),
        edge_distribution=(0.8, 1.2),
    )
    second_policy = uniform(
        node_assets="cpu",
        edge_assets="latency",
        node_distribution=(0.8, 1.2),
        edge_distribution=(0.8, 1.2),
    )

    first_policy(first_graph)
    second_policy(second_graph)

    assert first_graph.nodes["a"]["cpu"] == second_graph.nodes["a"]["cpu"]
    assert (
        first_graph.edges["a", "b"]["latency"]
        == second_graph.edges["a", "b"]["latency"]
    )


def test_normal_distribution_policy_applies_selected_gaussian_multipliers():
    graph = build_graph()

    normal(
        node_assets="cpu",
        edge_assets="bandwidth",
        node_distribution=(1.5, 0.0),
        edge_distribution=(0.5, 0.0),
    )(graph)

    assert graph.nodes["a"]["cpu"] == 120
    assert graph.nodes["a"]["ram"] == 32
    assert graph.edges["a", "b"]["bandwidth"] == 50
    assert graph.edges["a", "b"]["latency"] == 10


def test_normal_distribution_policy_validates_std_and_supports_per_asset_overrides():
    with pytest.raises(ValueError):
        normal(node_distribution=(1.0, -0.1))

    graph = build_graph()
    normal(
        node_asset_distributions={"cpu": (0.5, 0.0)},
        edge_asset_distributions={"latency": (2.0, 0.0)},
    )(graph)

    assert graph.nodes["a"]["cpu"] == 40
    assert graph.nodes["a"]["ram"] == 32
    assert graph.edges["a", "b"]["latency"] == 20
    assert graph.edges["a", "b"]["bandwidth"] == 100


def test_normal_distribution_uses_graph_rng_reproducibly():
    first_graph = build_graph()
    second_graph = build_graph()

    first_policy = normal(
        node_assets="cpu",
        edge_assets="latency",
        node_distribution=(1.0, 0.1),
        edge_distribution=(1.0, 0.1),
    )
    second_policy = normal(
        node_assets="cpu",
        edge_assets="latency",
        node_distribution=(1.0, 0.1),
        edge_distribution=(1.0, 0.1),
    )

    first_policy(first_graph)
    second_policy(second_graph)

    assert first_graph.nodes["a"]["cpu"] == second_graph.nodes["a"]["cpu"]
    assert (
        first_graph.edges["a", "b"]["latency"]
        == second_graph.edges["a", "b"]["latency"]
    )


def test_lognormal_distribution_policy_applies_selected_multipliers():
    graph = build_graph()

    lognormal(
        node_assets="cpu",
        edge_assets="bandwidth",
        node_distribution=(math.log(1.5), 0.0),
        edge_distribution=(math.log(0.5), 0.0),
    )(graph)

    assert graph.nodes["a"]["cpu"] == 120
    assert graph.edges["a", "b"]["bandwidth"] == 50


def test_lognormal_distribution_validates_sigma():
    with pytest.raises(ValueError):
        lognormal(node_distribution=(0.0, -0.1))


def test_beta_distribution_uses_graph_rng_reproducibly():
    first_graph = build_graph()
    second_graph = build_graph()

    first_policy = beta(
        node_assets="cpu",
        edge_assets="latency",
        node_distribution=(2.0, 3.0),
        edge_distribution=(2.0, 3.0),
    )
    second_policy = beta(
        node_assets="cpu",
        edge_assets="latency",
        node_distribution=(2.0, 3.0),
        edge_distribution=(2.0, 3.0),
    )

    first_policy(first_graph)
    second_policy(second_graph)

    assert first_graph.nodes["a"]["cpu"] == second_graph.nodes["a"]["cpu"]
    assert (
        first_graph.edges["a", "b"]["latency"]
        == second_graph.edges["a", "b"]["latency"]
    )


def test_beta_distribution_validates_parameters():
    with pytest.raises(ValueError):
        beta(node_distribution=(0.0, 1.0))


def test_gamma_distribution_uses_graph_rng_reproducibly():
    first_graph = build_graph()
    second_graph = build_graph()

    first_policy = gamma(
        node_assets="cpu",
        edge_assets="latency",
        node_distribution=(2.0, 0.5),
        edge_distribution=(2.0, 0.5),
    )
    second_policy = gamma(
        node_assets="cpu",
        edge_assets="latency",
        node_distribution=(2.0, 0.5),
        edge_distribution=(2.0, 0.5),
    )

    first_policy(first_graph)
    second_policy(second_graph)

    assert first_graph.nodes["a"]["cpu"] == second_graph.nodes["a"]["cpu"]
    assert (
        first_graph.edges["a", "b"]["latency"]
        == second_graph.edges["a", "b"]["latency"]
    )


def test_gamma_distribution_validates_parameters():
    with pytest.raises(ValueError):
        gamma(node_distribution=(-1.0, 1.0))


def test_triangular_distribution_applies_selected_multipliers():
    graph = build_graph()

    triangular(
        node_assets="cpu",
        edge_assets="bandwidth",
        node_distribution=(1.5, 1.5, 1.5),
        edge_distribution=(0.5, 0.5, 0.5),
    )(graph)

    assert graph.nodes["a"]["cpu"] == 120
    assert graph.edges["a", "b"]["bandwidth"] == 50


def test_triangular_distribution_validates_shape():
    with pytest.raises(ValueError):
        triangular(node_distribution=(2.0, 1.0, 1.5))

    with pytest.raises(ValueError):
        triangular(node_distribution=(1.0, 2.0, 3.0))


def test_truncated_normal_distribution_applies_selected_multipliers():
    graph = build_graph()

    truncated_normal(
        node_assets="cpu",
        edge_assets="bandwidth",
        node_distribution=(1.5, 0.0),
        edge_distribution=(0.5, 0.0),
        lower=0.0,
        upper=2.0,
    )(graph)

    assert graph.nodes["a"]["cpu"] == 120
    assert graph.edges["a", "b"]["bandwidth"] == 50


def test_truncated_normal_distribution_validates_bounds():
    with pytest.raises(ValueError):
        truncated_normal(node_distribution=(1.0, -0.1))

    with pytest.raises(ValueError):
        truncated_normal(lower=2.0, upper=1.0)

    with pytest.raises(ValueError):
        truncated_normal(max_attempts=0)


def test_categorical_distribution_applies_selected_multipliers():
    graph = build_graph()

    categorical(
        node_assets="cpu",
        edge_assets="bandwidth",
        node_distribution=[1.5],
        edge_distribution=[0.5],
    )(graph)

    assert graph.nodes["a"]["cpu"] == 120
    assert graph.edges["a", "b"]["bandwidth"] == 50


def test_categorical_distribution_supports_weights_and_overrides():
    graph = build_graph()

    categorical(
        node_asset_distributions={"cpu": [0.5, 1.5]},
        edge_asset_distributions={"latency": [2.0]},
        node_asset_weights={"cpu": [1.0, 0.0]},
        edge_asset_weights={"latency": [1.0]},
    )(graph)

    assert graph.nodes["a"]["cpu"] == 40
    assert graph.nodes["a"]["ram"] == 32
    assert graph.edges["a", "b"]["latency"] == 20


def test_categorical_distribution_validates_inputs():
    with pytest.raises(ValueError):
        categorical(node_distribution=[])

    with pytest.raises(ValueError):
        categorical(node_weights=[1.0, 2.0])

    with pytest.raises(ValueError):
        categorical(node_distribution=[1.0], node_weights=[-1.0])

    with pytest.raises(ValueError):
        categorical(node_distribution=[1.0], node_weights=[0.0])

    with pytest.raises(ValueError):
        categorical(node_asset_weights={"cpu": [1.0]})
