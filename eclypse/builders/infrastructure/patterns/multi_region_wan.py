"""Multi-region WAN infrastructure pattern.

The multi-region WAN pattern models several compute regions connected by a slower
backbone, with each region containing local compute nodes behind a regional
gateway. The architecture proposes two layers inside each region, a gateway and
its attached regional nodes, and then a WAN backbone between gateways.

This captures the QoS asymmetry of geo-distributed deployments: intra-region
links are relatively fast and high-bandwidth, while inter-region communication
is costlier in latency and capacity, making the pattern useful for placement and
replication studies across distant sites.
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


def get_multi_region_wan(
    region_count: int,
    nodes_per_region: int,
    infrastructure_id: str = "multi_region_wan",
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
    """Create a multi-region WAN with per-region gateways and local compute nodes.

    Args:
        region_count (int):
            Number of regions in the topology.
        nodes_per_region (int):
            Number of compute nodes attached to each region.
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
        Infrastructure: The generated multi-region WAN.

    Raises:
        ValueError: If no region is requested.
    """
    if region_count <= 0:
        raise ValueError("The multi-region WAN requires at least one region.")

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

    gateways = [f"region_{region}_gateway" for region in range(region_count)]
    add_nodes(
        infrastructure,
        gateways,
        strict=strict,
        **tier_node_assets(
            infrastructure,
            cpu=8.0,
            ram=16.0,
            storage=64.0,
            availability=0.995,
            processing_time=2.0,
        ),
    )

    local_link = tier_link_assets(infrastructure, latency=2.0, bandwidth=1000.0)
    wan_link = tier_link_assets(infrastructure, latency=35.0, bandwidth=300.0)
    for region in range(region_count):
        region_nodes = [
            f"region_{region}_node_{index}" for index in range(nodes_per_region)
        ]
        add_nodes(
            infrastructure,
            region_nodes,
            strict=strict,
            **tier_node_assets(
                infrastructure,
                cpu=16.0,
                gpu=1.0,
                ram=32.0,
                storage=256.0,
                availability=0.99,
                processing_time=3.0,
            ),
        )
        connect_round_robin(
            infrastructure,
            region_nodes,
            [gateways[region]],
            symmetric=symmetric,
            strict=strict,
            **local_link,
        )

    connect_clique(
        infrastructure,
        gateways,
        symmetric=symmetric,
        strict=strict,
        **wan_link,
    )
    return infrastructure
