from __future__ import annotations

import pytest

from eclypse.builders.infrastructure import (
    get_continuum_tiered,
    get_factory_cells,
    get_industrial_tsn,
    get_mec_5g,
    get_multi_region_wan,
    get_vehicular_edge,
)


def test_continuum_tiered():
    infrastructure = get_continuum_tiered(
        device_count=4,
        edge_count=2,
        fog_count=1,
        cloud_count=1,
        include_default_assets=True,
        seed=5,
    )

    assert any(node.startswith("device_") for node in infrastructure.nodes)
    assert any(node.startswith("edge_") for node in infrastructure.nodes)
    assert any(node.startswith("fog_") for node in infrastructure.nodes)
    assert any(node.startswith("cloud_") for node in infrastructure.nodes)
    assert infrastructure.nodes["cloud_0"]["processing_time"] == 1.0
    assert infrastructure.nodes["device_0"]["processing_time"] == 8.0

    custom_infrastructure = get_continuum_tiered(
        device_count=2,
        edge_count=1,
        fog_count=0,
        cloud_count=1,
        connectivity=[0.5, 1.0],
        cross_level_connectivity=[0.1, 0.2, 0.3],
        include_default_assets=True,
        seed=5,
    )
    assert len(custom_infrastructure.nodes) == 4

    with pytest.raises(ValueError, match="At least one tier"):
        get_continuum_tiered(0, 0, 0, 0)
    with pytest.raises(ValueError, match="non-negative"):
        get_continuum_tiered(-1, 1)


def test_mec_5g():
    infrastructure = get_mec_5g(
        user_count=4,
        ran_count=2,
        mec_count=2,
        cloud_count=1,
        include_default_assets=True,
    )

    assert "user_0" in infrastructure.nodes
    assert "ran_0" in infrastructure.nodes
    assert "mec_0" in infrastructure.nodes
    assert "cloud_0" in infrastructure.nodes
    assert infrastructure.has_edge("user_0", "ran_0")
    assert infrastructure.has_edge("ran_0", "mec_0")
    assert infrastructure.has_edge("mec_0", "cloud_0")

    with pytest.raises(ValueError, match="RAN"):
        get_mec_5g(user_count=1, ran_count=0)
    with pytest.raises(ValueError, match="MEC host"):
        get_mec_5g(user_count=1, ran_count=1, mec_count=0)


def test_multi_region_wan():
    infrastructure = get_multi_region_wan(
        region_count=2,
        nodes_per_region=3,
        path_algorithm=lambda graph, source, target: [source, target],
        include_default_assets=True,
    )

    assert "region_0_gateway" in infrastructure.nodes
    assert "region_1_gateway" in infrastructure.nodes
    assert "region_0_node_0" in infrastructure.nodes
    assert infrastructure.has_edge("region_0_gateway", "region_1_gateway")
    assert infrastructure.has_edge("region_0_node_0", "region_0_gateway")

    with pytest.raises(ValueError, match="region"):
        get_multi_region_wan(region_count=0, nodes_per_region=1)


def test_industrial_tsn():
    infrastructure = get_industrial_tsn(
        endpoint_count=4,
        switch_count=2,
        controller_count=1,
        edge_count=1,
        include_default_assets=True,
    )

    assert "switch_0" in infrastructure.nodes
    assert "controller_0" in infrastructure.nodes
    assert "endpoint_0" in infrastructure.nodes
    assert infrastructure.has_edge("switch_0", "switch_1")

    with pytest.raises(ValueError, match="switch"):
        get_industrial_tsn(endpoint_count=1, switch_count=0)


def test_factory_cells():
    infrastructure = get_factory_cells(
        cell_count=2,
        machines_per_cell=2,
        sensors_per_cell=2,
        plant_edge_count=1,
        cloud_count=1,
        include_default_assets=True,
    )

    assert "cell_0_controller" in infrastructure.nodes
    assert "cell_1_machine_0" in infrastructure.nodes
    assert "plant_edge_0" in infrastructure.nodes
    assert infrastructure.has_edge("cell_0_controller", "plant_edge_0")
    assert infrastructure.has_edge("plant_edge_0", "cloud_0")

    with pytest.raises(ValueError, match="cell"):
        get_factory_cells(cell_count=0, machines_per_cell=1, sensors_per_cell=1)


def test_vehicular_edge():
    infrastructure = get_vehicular_edge(
        vehicle_count=4,
        rsu_count=2,
        mec_count=1,
        cloud_count=1,
        include_default_assets=True,
    )

    assert "vehicle_0" in infrastructure.nodes
    assert "rsu_0" in infrastructure.nodes
    assert "mec_0" in infrastructure.nodes
    assert infrastructure.has_edge("vehicle_0", "rsu_0")
    assert infrastructure.has_edge("rsu_0", "mec_0")

    with pytest.raises(ValueError, match="RSU"):
        get_vehicular_edge(vehicle_count=1, rsu_count=0)
    with pytest.raises(ValueError, match="MEC host"):
        get_vehicular_edge(vehicle_count=1, rsu_count=1, mec_count=0)
