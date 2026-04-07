from __future__ import annotations

import pytest

from eclypse.builders import application as application_builders
from eclypse.builders import infrastructure as infrastructure_builders
from eclypse.builders.application import get_sock_shop
from eclypse.builders.infrastructure import get_orion_cev
from eclypse.builders.infrastructure.generators.b_cube import b_cube
from eclypse.builders.infrastructure.generators.fat_tree import fat_tree
from eclypse.builders.infrastructure.generators.hierarchical import (
    _get_connectivity_functions,
    _uniform_level_connectivity,
    hierarchical,
)
from eclypse.builders.infrastructure.generators.random import random
from eclypse.builders.infrastructure.generators.star import star
from eclypse.remote.service.service import Service


def test_builder_exports_are_available():
    assert callable(application_builders.get_sock_shop)
    assert callable(infrastructure_builders.get_orion_cev)


def test_star_random_and_hierarchical_generators_build_expected_topologies():
    star_infra = star(
        3,
        symmetric=True,
        include_default_assets=True,
        center_assets_values={"cpu": 9},
        outer_assets_values={"cpu": 1},
    )
    random_infra = random(3, p=1.0, symmetric=True, seed=7)
    hierarchy = hierarchical(
        4,
        node_partitioning=[0.5, 0.5],
        connectivity=[1.0],
        cross_level_connectivity=[0.0, 0.0],
        seed=3,
    )

    assert set(star_infra.nodes) == {"center", "outer_0", "outer_1", "outer_2"}
    assert star_infra.nodes["center"]["cpu"] == 9
    assert len(star_infra.edges) == 6
    assert len(random_infra.edges) == 6
    assert len(hierarchy.nodes) == 4
    assert any(node.startswith("l0_") for node in hierarchy.nodes)
    assert any(node.startswith("l1_") for node in hierarchy.nodes)
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


def test_fat_tree_b_cube_orion_and_sock_shop_builders():
    with pytest.raises(ValueError, match="even number"):
        fat_tree(3)

    fat_tree_infra = fat_tree(2)
    bcube_infra = b_cube(1, 2)
    orion = get_orion_cev(include_default_assets=True)
    sock_shop = get_sock_shop(include_default_assets=True)
    remote_sock_shop = get_sock_shop(
        include_default_assets=True,
        communication_interface="mpi",
    )
    rest_sock_shop = get_sock_shop(
        include_default_assets=True,
        communication_interface="rest",
        flows=[["FrontendService", "CatalogService"]],
    )

    assert len(fat_tree_infra.nodes) == 7
    assert len(fat_tree_infra.edges) == 12
    assert len(bcube_infra.nodes) == 7
    assert len(bcube_infra.edges) == 12
    assert "DU11" in orion.nodes
    assert orion.has_edge("DU11", "NS11")
    assert orion.nodes["NS11"]["processing_time"] == 1
    assert sock_shop.has_logic is False
    assert remote_sock_shop.has_logic is True
    assert rest_sock_shop.has_logic is True
    assert all(
        isinstance(service, Service) for service in remote_sock_shop.services.values()
    )
    assert all(
        isinstance(service, Service) for service in rest_sock_shop.services.values()
    )
    assert sock_shop.has_edge("FrontendService", "CatalogService")
    assert sock_shop.has_edge("CatalogService", "FrontendService")
    assert len(sock_shop.flows) == 5
    assert rest_sock_shop.flows == [["FrontendService", "CatalogService"]]

    with pytest.raises(ValueError, match="Unknown communication interface"):
        get_sock_shop(communication_interface="grpc")  # type: ignore[arg-type]
