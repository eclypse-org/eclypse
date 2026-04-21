"""MEC 5G infrastructure pattern.

The MEC 5G pattern models user equipment attached to radio sites, each backed by
edge compute close to the access network and connected onward to a cloud tier.
The proposed layers are user equipment, radio access nodes, MEC hosts, and
cloud nodes. Vehicles or mobile users attach to the radio tier, the radio tier
uplinks to nearby MEC compute, and MEC nodes connect to a more distant cloud.

The built-in QoS profile reflects this structure: access links favour low
latency and moderate bandwidth, backhaul links are faster and more stable, and
the cloud uplink trades proximity for larger aggregate capacity.
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
    from eclypse.placement.strategies import PlacementStrategy
    from eclypse.utils.types import (
        InitPolicy,
        UpdatePolicies,
    )


def mec_5g(
    user_count: int,
    ran_count: int,
    mec_count: int | None = None,
    cloud_count: int = 1,
    infrastructure_id: str = "mec_5g",
    symmetric: bool = True,
    update_policies: UpdatePolicies = None,
    node_assets: dict[str, Asset] | None = None,
    link_assets: dict[str, Asset] | None = None,
    include_default_assets: bool = False,
    strict: bool = False,
    resource_init: InitPolicy = "max",
    placement_strategy: PlacementStrategy | None = None,
    path_algorithm: Callable[[nx.Graph, str, str], list[str]] | None = None,
    seed: int | None = None,
) -> Infrastructure:
    """Create a 5G edge infrastructure with radio access, MEC, and cloud tiers.

    Args:
        user_count (int):
            Number of user-equipment nodes.
        ran_count (int):
            Number of radio access sites.
        mec_count (int | None):
            Number of MEC hosts. Defaults to ``ran_count``.
        cloud_count (int):
            Number of cloud nodes.
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
        placement_strategy (PlacementStrategy | None):
            Optional placement strategy attached to the infrastructure.
        path_algorithm (Callable[[nx.Graph, str, str], list[str]] | None):
            Path computation function for infrastructure routing.
        seed (int | None):
            Seed forwarded to the infrastructure random generator.

    Returns:
        Infrastructure: The generated MEC 5G infrastructure.

    Raises:
        ValueError: If the required radio access or MEC tiers are missing.
    """
    mec_total = ran_count if mec_count is None else mec_count
    if ran_count <= 0:
        raise ValueError("The MEC 5G pattern requires at least one RAN site.")
    if mec_total <= 0:
        raise ValueError("The MEC 5G pattern requires at least one MEC host.")

    infrastructure = Infrastructure(
        infrastructure_id=infrastructure_id,
        update_policies=update_policies,
        node_assets=node_assets,
        edge_assets=link_assets,
        include_default_assets=include_default_assets,
        resource_init=resource_init,
        path_algorithm=path_algorithm,
        placement_strategy=placement_strategy,
        seed=seed,
    )

    users = [f"user_{index}" for index in range(user_count)]
    rans = [f"ran_{index}" for index in range(ran_count)]
    mecs = [f"mec_{index}" for index in range(mec_total)]
    clouds = [f"cloud_{index}" for index in range(cloud_count)]

    add_nodes(
        infrastructure,
        users,
        strict=strict,
        **tier_node_assets(
            infrastructure,
            cpu=1.0,
            ram=1.0,
            storage=1.0,
            availability=0.95,
            processing_time=8.0,
        ),
    )
    add_nodes(
        infrastructure,
        rans,
        strict=strict,
        **tier_node_assets(
            infrastructure,
            cpu=2.0,
            ram=4.0,
            storage=8.0,
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
            storage=256.0,
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

    access_link = tier_link_assets(infrastructure, latency=5.0, bandwidth=200.0)
    backhaul_link = tier_link_assets(infrastructure, latency=2.0, bandwidth=1000.0)
    wan_link = tier_link_assets(infrastructure, latency=20.0, bandwidth=500.0)

    connect_round_robin(
        infrastructure,
        users,
        rans,
        symmetric=symmetric,
        strict=strict,
        **access_link,
    )
    connect_round_robin(
        infrastructure,
        rans,
        mecs,
        symmetric=symmetric,
        strict=strict,
        **backhaul_link,
    )
    connect_round_robin(
        infrastructure,
        mecs,
        clouds,
        symmetric=symmetric,
        strict=strict,
        **wan_link,
    )
    connect_clique(
        infrastructure,
        clouds,
        symmetric=symmetric,
        strict=strict,
        **tier_link_assets(infrastructure, latency=5.0, bandwidth=2000.0),
    )

    return infrastructure
