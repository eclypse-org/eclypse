"""Vehicular-edge infrastructure pattern.

The vehicular-edge pattern models vehicles attached to roadside units, backed by MEC
hosts and an optional cloud tier. The proposed layers are vehicles, roadside
units, MEC hosts, and cloud nodes. Vehicles attach to nearby roadside units,
roadside units forward traffic to edge compute, and MEC nodes connect onward to
the cloud for less latency-sensitive processing.

Its QoS profile reflects connected-mobility assumptions: access links favour low
latency but limited bandwidth, roadside and MEC links provide stronger local
capacity, and the cloud uplink captures the longer-latency control or archival
path.
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


def get_vehicular_edge(
    vehicle_count: int,
    rsu_count: int,
    mec_count: int = 1,
    cloud_count: int = 1,
    infrastructure_id: str = "vehicular_edge",
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
    """Create a vehicular-edge topology with RSUs, MEC, and cloud tiers.

    Args:
        vehicle_count (int):
            Number of vehicle nodes.
        rsu_count (int):
            Number of roadside units.
        mec_count (int):
            Number of MEC hosts serving the roadside tier.
        cloud_count (int):
            Number of cloud nodes attached to MEC.
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
        Infrastructure: The generated vehicular-edge infrastructure.

    Raises:
        ValueError: If the topology misses roadside or MEC nodes.
    """
    if rsu_count <= 0:
        raise ValueError("The vehicular-edge pattern requires at least one RSU.")
    if mec_count <= 0:
        raise ValueError("The vehicular-edge pattern requires at least one MEC host.")

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

    vehicles = [f"vehicle_{index}" for index in range(vehicle_count)]
    rsus = [f"rsu_{index}" for index in range(rsu_count)]
    mecs = [f"mec_{index}" for index in range(mec_count)]
    clouds = [f"cloud_{index}" for index in range(cloud_count)]

    add_nodes(
        infrastructure,
        vehicles,
        strict=strict,
        **tier_node_assets(
            infrastructure,
            cpu=2.0,
            ram=2.0,
            storage=4.0,
            availability=0.94,
            processing_time=7.0,
        ),
    )
    add_nodes(
        infrastructure,
        rsus,
        strict=strict,
        **tier_node_assets(
            infrastructure,
            cpu=4.0,
            ram=8.0,
            storage=16.0,
            availability=0.98,
            processing_time=4.0,
        ),
    )
    add_nodes(
        infrastructure,
        mecs,
        strict=strict,
        **tier_node_assets(
            infrastructure,
            cpu=16.0,
            gpu=1.0,
            ram=32.0,
            storage=128.0,
            availability=0.99,
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

    connect_round_robin(
        infrastructure,
        vehicles,
        rsus,
        symmetric=symmetric,
        strict=strict,
        **tier_link_assets(infrastructure, latency=3.0, bandwidth=200.0),
    )
    connect_round_robin(
        infrastructure,
        rsus,
        mecs,
        symmetric=symmetric,
        strict=strict,
        **tier_link_assets(infrastructure, latency=5.0, bandwidth=500.0),
    )
    connect_round_robin(
        infrastructure,
        mecs,
        clouds,
        symmetric=symmetric,
        strict=strict,
        **tier_link_assets(infrastructure, latency=20.0, bandwidth=500.0),
    )
    connect_clique(
        infrastructure,
        rsus,
        symmetric=symmetric,
        strict=strict,
        **tier_link_assets(infrastructure, latency=8.0, bandwidth=250.0),
    )
    return infrastructure
