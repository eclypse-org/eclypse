from __future__ import annotations

import pytest

from eclypse.builders.infrastructure._helpers import connect_round_robin
from eclypse.builders.infrastructure.generators.b_cube import b_cube
from eclypse.builders.infrastructure.generators.fat_tree import fat_tree
from eclypse.builders.infrastructure.generators.hierarchical import (
    _get_connectivity_functions,
    _uniform_level_connectivity,
    hierarchical,
)
from eclypse.builders.infrastructure.generators.random import random
from eclypse.builders.infrastructure.generators.scale_free import scale_free
from eclypse.builders.infrastructure.generators.small_world import small_world
from eclypse.builders.infrastructure.generators.star import star
from eclypse.graph import Infrastructure


def test_star():
    infrastructure = star(
        3,
        symmetric=True,
        include_default_assets=True,
        center_assets_values={"cpu": 9},
        outer_assets_values={"cpu": 1},
    )

    assert set(infrastructure.nodes) == {"center", "outer_0", "outer_1", "outer_2"}
    assert infrastructure.nodes["center"]["cpu"] == 9
    assert len(infrastructure.edges) == 6


def test_random():
    infrastructure = random(3, p=1.0, symmetric=True, seed=7)

    assert len(infrastructure.nodes) == 3
    assert len(infrastructure.edges) == 6


def test_hierarchical():
    infrastructure = hierarchical(
        4,
        node_partitioning=[0.5, 0.5],
        connectivity=[1.0],
        cross_level_connectivity=[0.0, 0.0],
        seed=3,
    )
    default_infrastructure = hierarchical(20, seed=3)

    assert len(infrastructure.nodes) == 4
    assert len(default_infrastructure.nodes) == 20
    assert any(node.startswith("l0_") for node in infrastructure.nodes)
    assert any(node.startswith("l1_") for node in infrastructure.nodes)
    assert any(node.startswith("l0_") for node in default_infrastructure.nodes)
    assert list(_uniform_level_connectivity(["a"], ["b", "c"], p=0.0, seed=1)) == [
        ("a", "b"),
        ("a", "c"),
    ]
    assert (
        len(_get_connectivity_functions(length=2, connectivity=lambda *_args: iter(())))
        == 2
    )

    with pytest.raises(ValueError, match="sum of the node distribution"):
        hierarchical(4, node_partitioning=[0.4, 0.4])

    with pytest.raises(ValueError, match="function for each level"):
        _get_connectivity_functions(connectivity=[1.0], length=2)
    with pytest.raises(ValueError, match="function or a list"):
        _get_connectivity_functions(connectivity=1.0, length=1)


def test_fat_tree():
    with pytest.raises(ValueError, match="even number"):
        fat_tree(3)

    infrastructure = fat_tree(2)

    assert len(infrastructure.nodes) == 7
    assert len(infrastructure.edges) == 12


def test_b_cube():
    infrastructure = b_cube(1, 2)

    assert len(infrastructure.nodes) == 7
    assert len(infrastructure.edges) == 12


def test_small_world():
    infrastructure = small_world(6, k=2, p=0.0, symmetric=True, seed=7)

    assert len(infrastructure.nodes) == 6
    assert all(node.startswith("n") for node in infrastructure.nodes)
    assert len(infrastructure.edges) == 12


def test_scale_free():
    infrastructure = scale_free(6, m=1, symmetric=True, seed=3)
    helper_infrastructure = Infrastructure()
    helper_infrastructure.add_node("source")

    assert len(infrastructure.nodes) == 6
    assert all(node.startswith("n") for node in infrastructure.nodes)
    assert len(infrastructure.edges) >= 10

    with pytest.raises(ValueError, match="At least one target node"):
        connect_round_robin(helper_infrastructure, ["source"], [])
