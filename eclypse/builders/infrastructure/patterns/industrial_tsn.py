"""Industrial TSN infrastructure pattern.

The industrial TSN pattern models a deterministic switched LAN for controllers,
field devices, and local edge compute in industrial automation settings. It
proposes a switching fabric at the centre, with endpoints, controllers, and
plant-edge compute attached to the same deterministic network.

The featured QoS assumption is strict and predictable service quality: TSN links
represent low-latency, high-bandwidth paths intended for bounded-delay control
traffic, while the switching fabric provides deterministic connectivity between
control and production nodes instead of best-effort routing.
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


def get_industrial_tsn(
    endpoint_count: int,
    switch_count: int = 2,
    controller_count: int = 2,
    edge_count: int = 1,
    infrastructure_id: str = "industrial_tsn",
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
    """Create an industrial TSN LAN with switches, controllers, and endpoints.

    Args:
        endpoint_count (int):
            Number of field endpoints connected to the TSN network.
        switch_count (int):
            Number of industrial switches.
        controller_count (int):
            Number of control nodes.
        edge_count (int):
            Number of edge-compute nodes on the plant LAN.
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
        Infrastructure: The generated industrial TSN infrastructure.

    Raises:
        ValueError: If the topology misses its switching fabric.
    """
    if switch_count <= 0:
        raise ValueError("The industrial TSN pattern requires at least one switch.")

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

    endpoints = [f"endpoint_{index}" for index in range(endpoint_count)]
    switches = [f"switch_{index}" for index in range(switch_count)]
    controllers = [f"controller_{index}" for index in range(controller_count)]
    edges = [f"edge_{index}" for index in range(edge_count)]

    add_nodes(
        infrastructure,
        endpoints,
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
    add_nodes(
        infrastructure,
        switches,
        strict=strict,
        **tier_node_assets(
            infrastructure,
            cpu=2.0,
            ram=2.0,
            storage=8.0,
            availability=0.999,
            processing_time=1.0,
        ),
    )
    add_nodes(
        infrastructure,
        controllers,
        strict=strict,
        **tier_node_assets(
            infrastructure,
            cpu=8.0,
            ram=8.0,
            storage=32.0,
            availability=0.995,
            processing_time=2.0,
        ),
    )
    add_nodes(
        infrastructure,
        edges,
        strict=strict,
        **tier_node_assets(
            infrastructure,
            cpu=16.0,
            gpu=1.0,
            ram=32.0,
            storage=128.0,
            availability=0.995,
            processing_time=2.0,
        ),
    )

    tsn_link = tier_link_assets(infrastructure, latency=0.5, bandwidth=1000.0)
    backbone_link = tier_link_assets(infrastructure, latency=1.0, bandwidth=2000.0)

    connect_round_robin(
        infrastructure,
        endpoints,
        switches,
        symmetric=symmetric,
        strict=strict,
        **tsn_link,
    )
    connect_round_robin(
        infrastructure,
        controllers,
        switches,
        symmetric=symmetric,
        strict=strict,
        **backbone_link,
    )
    connect_round_robin(
        infrastructure,
        edges,
        switches,
        symmetric=symmetric,
        strict=strict,
        **backbone_link,
    )
    connect_clique(
        infrastructure,
        switches,
        symmetric=symmetric,
        strict=strict,
        **backbone_link,
    )
    return infrastructure
