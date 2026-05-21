"""Factory-cells infrastructure pattern.

The factory-cells pattern models repeated production cells connected to plant-edge
compute, suitable for industrial monitoring and assembly workloads. Each cell is
organised around a local controller with its machines and sensors, while one or more
plant-edge nodes aggregate traffic across cells and optionally uplink to a cloud tier.

The pattern combines two QoS domains: short, high-quality local links inside a cell for
operational traffic, and slower uplinks from cells to plant-edge or cloud resources for
coordination, analytics, or historical storage.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from eclypse.builders.infrastructure._helpers import (
    add_nodes,
    connect_clique,
    connect_round_robin,
    tier_link_assets,
    tier_node_assets,
)
from eclypse.graph import Infrastructure

if TYPE_CHECKING:
    from collections.abc import Callable

    import networkx as nx

    from eclypse.graph.assets import Asset
    from eclypse.utils.types import (
        InitPolicy,
        UpdatePolicies,
    )


def get_factory_cells(
    cell_count: int,
    machines_per_cell: int,
    sensors_per_cell: int,
    plant_edge_count: int = 1,
    cloud_count: int = 1,
    infrastructure_id: str = "factory_cells",
    symmetric: bool = True,
    update_policies: UpdatePolicies = None,
    node_assets: dict[str, Asset] | None = None,
    link_assets: dict[str, Asset] | None = None,
    include_default_assets: bool = False,
    strict: bool = False,
    resource_init: InitPolicy = "max",
    path_algorithm: Callable[[nx.Graph, str, str], list[str]] | None = None,
    seed: int | None = None,
) -> Infrastructure:
    """Create a smart-factory topology organised into repeated production cells.

    Args:
        cell_count (int):
            Number of production cells.
        machines_per_cell (int):
            Number of machine nodes per cell.
        sensors_per_cell (int):
            Number of sensor nodes per cell.
        plant_edge_count (int):
            Number of plant-edge nodes shared across cells.
        cloud_count (int):
            Number of cloud nodes attached to the plant edge.
        infrastructure_id (str):
            Identifier assigned to the infrastructure.
        symmetric (bool):
            Whether generated links should be mirrored.
        update_policies (UpdatePolicies):
            Graph update policies executed during ``evolve()``.
        node_assets (dict[str, Asset] | None):
            Node asset definitions available to the infrastructure.
        link_assets (dict[str, Asset] | None):
            Edge asset definitions available to the infrastructure.
        include_default_assets (bool):
            Whether to include default ECLYPSE assets.
        strict (bool):
            Whether inconsistent asset values should raise.
        resource_init (InitPolicy):
            Initialisation policy used for graph assets.
        path_algorithm (Callable[[nx.Graph, str, str], list[str]] | None):
            Path computation function for infrastructure routing.
        seed (int | None):
            Seed forwarded to the infrastructure random generator.

    Returns:
        Infrastructure: The generated factory-cells infrastructure.

    Raises:
        ValueError: If no production cell is requested.
    """
    if cell_count <= 0:
        raise ValueError("The factory-cells pattern requires at least one cell.")

    infrastructure = Infrastructure(
        infrastructure_id=infrastructure_id,
        update_policies=update_policies,
        node_assets=node_assets,
        edge_assets=link_assets,
        include_default_assets=include_default_assets,
        resource_init=resource_init,
        path_algorithm=path_algorithm,
        seed=seed,
    )

    plant_edges = [f"plant_edge_{index}" for index in range(plant_edge_count)]
    clouds = [f"cloud_{index}" for index in range(cloud_count)]
    add_nodes(
        infrastructure,
        plant_edges,
        strict=strict,
        **tier_node_assets(
            infrastructure,
            cpu=24.0,
            gpu=2.0,
            ram=64.0,
            storage=512.0,
            availability=0.995,
            processing_time=2.0,
        ),
    )
    add_nodes(
        infrastructure,
        clouds,
        strict=strict,
        **tier_node_assets(
            infrastructure,
            cpu=32.0,
            gpu=4.0,
            ram=128.0,
            storage=1024.0,
            availability=0.999,
            processing_time=1.0,
        ),
    )

    cell_link = tier_link_assets(infrastructure, latency=1.0, bandwidth=1000.0)
    uplink = tier_link_assets(infrastructure, latency=8.0, bandwidth=500.0)
    for cell_index in range(cell_count):
        controller = [f"cell_{cell_index}_controller"]
        machines = [
            f"cell_{cell_index}_machine_{index}" for index in range(machines_per_cell)
        ]
        sensors = [
            f"cell_{cell_index}_sensor_{index}" for index in range(sensors_per_cell)
        ]
        add_nodes(
            infrastructure,
            controller,
            strict=strict,
            **tier_node_assets(
                infrastructure,
                cpu=8.0,
                ram=8.0,
                storage=32.0,
                availability=0.99,
                processing_time=3.0,
            ),
        )
        add_nodes(
            infrastructure,
            machines,
            strict=strict,
            **tier_node_assets(
                infrastructure,
                cpu=4.0,
                ram=4.0,
                storage=16.0,
                availability=0.98,
                processing_time=4.0,
            ),
        )
        add_nodes(
            infrastructure,
            sensors,
            strict=strict,
            **tier_node_assets(
                infrastructure,
                cpu=1.0,
                ram=1.0,
                storage=2.0,
                availability=0.97,
                processing_time=6.0,
            ),
        )
        connect_round_robin(
            infrastructure,
            machines + sensors,
            controller,
            symmetric=symmetric,
            strict=strict,
            **cell_link,
        )
        connect_round_robin(
            infrastructure,
            controller,
            plant_edges,
            symmetric=symmetric,
            strict=strict,
            **uplink,
        )

    connect_clique(
        infrastructure,
        plant_edges,
        symmetric=symmetric,
        strict=strict,
        **tier_link_assets(infrastructure, latency=2.0, bandwidth=2000.0),
    )
    connect_round_robin(
        infrastructure,
        plant_edges,
        clouds,
        symmetric=symmetric,
        strict=strict,
        **tier_link_assets(infrastructure, latency=15.0, bandwidth=1000.0),
    )
    return infrastructure
