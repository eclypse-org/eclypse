from __future__ import annotations

import pytest

from eclypse.builders.infrastructure._helpers import connect_round_robin
from eclypse.builders.infrastructure import (
    get_b_cube,
    get_fat_tree,
    get_hierarchical,
    get_random,
    get_scale_free,
    get_small_world,
    get_star,
)
from eclypse.builders.infrastructure.generators.hierarchical import (
    _get_connectivity_functions,
    _uniform_level_connectivity,
)
from eclypse.graph import Infrastructure


def test_star():
    infrastructure = get_star(
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
    infrastructure = get_random(3, p=1.0, symmetric=True, seed=7)

    assert len(infrastructure.nodes) == 3
    assert len(infrastructure.edges) == 6


def test_hierarchical():
    infrastructure = get_hierarchical(
        4,
        node_partitioning=[0.5, 0.5],
        connectivity=[1.0],
        cross_level_connectivity=[0.0, 0.0],
        seed=3,
    )
    default_infrastructure = get_hierarchical(20, seed=3)

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
        get_hierarchical(4, node_partitioning=[0.4, 0.4])

    with pytest.raises(ValueError, match="function for each level"):
        _get_connectivity_functions(connectivity=[1.0], length=2)
    with pytest.raises(ValueError, match="function or a list"):
        _get_connectivity_functions(connectivity=1.0, length=1)


def test_fat_tree():
    with pytest.raises(ValueError, match="even number"):
        get_fat_tree(3)

    infrastructure = get_fat_tree(2)

    assert len(infrastructure.nodes) == 7
    assert len(infrastructure.edges) == 12


def test_b_cube():
    infrastructure = get_b_cube(1, 2)

    assert len(infrastructure.nodes) == 7
    assert len(infrastructure.edges) == 12


def test_small_world():
    infrastructure = get_small_world(6, k=2, p=0.0, symmetric=True, seed=7)

    assert len(infrastructure.nodes) == 6
    assert all(node.startswith("n") for node in infrastructure.nodes)
    assert len(infrastructure.edges) == 12


def test_scale_free():
    infrastructure = get_scale_free(6, m=1, symmetric=True, seed=3)
    helper_infrastructure = Infrastructure()
    helper_infrastructure.add_node("source")

    assert len(infrastructure.nodes) == 6
    assert all(node.startswith("n") for node in infrastructure.nodes)
    assert len(infrastructure.edges) >= 10

    with pytest.raises(ValueError, match="At least one target node"):
        connect_round_robin(helper_infrastructure, ["source"], [])
