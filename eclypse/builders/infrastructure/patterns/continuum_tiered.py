"""Continuum-tiered infrastructure pattern.

The continuum-tiered pattern models a device-edge-fog-cloud deployment by adapting the
generic hierarchical generator with tier-aware naming and resource defaults. It
proposes up to four semantic layers: device, edge, fog, and cloud. Nodes are
grouped by tier and connected primarily across adjacent layers, while the
intra-tier connectivity grows progressively richer from device to cloud.

The pattern is designed for continuum QoS studies where latency and capacity are
not uniform across the stack: devices are close to the data source but resource
poor, edge and fog tiers progressively improve compute and availability, and the
cloud tier offers the highest capacity with the loosest proximity guarantees.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from eclypse.builders.infrastructure._helpers import (
    relabel_hierarchical_levels,
    tier_node_assets,
)
from eclypse.builders.infrastructure.generators.hierarchical import hierarchical

if TYPE_CHECKING:
    from collections.abc import Callable

    import networkx as nx

    from eclypse.graph import Infrastructure
    from eclypse.graph.assets import Asset
    from eclypse.placement.strategies import PlacementStrategy
    from eclypse.utils.types import (
        InitPolicy,
        UpdatePolicies,
    )


def continuum_tiered(
    device_count: int,
    edge_count: int,
    fog_count: int = 0,
    cloud_count: int = 1,
    infrastructure_id: str = "continuum_tiered",
    symmetric: bool = True,
    connectivity: list[float] | None = None,
    cross_level_connectivity: list[float] | None = None,
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
    """Create an IoT-edge-cloud continuum from the hierarchical generator.

    Args:
        device_count (int):
            Number of device-tier nodes.
        edge_count (int):
            Number of edge-tier nodes.
        fog_count (int):
            Number of fog-tier nodes.
        cloud_count (int):
            Number of cloud-tier nodes.
        infrastructure_id (str):
            Identifier assigned to the infrastructure.
        symmetric (bool):
            Whether generated links should be mirrored.
        connectivity (list[float] | None):
            Cross-tier connectivity probabilities passed to ``hierarchical``.
        cross_level_connectivity (list[float] | None):
            Intra-tier connectivity probabilities passed to ``hierarchical``.
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
            Seed forwarded to the underlying hierarchical generator.

    Returns:
        Infrastructure: The generated continuum infrastructure.

    Raises:
        ValueError: If any tier count is negative or the total number of nodes is zero.
    """
    counts = {
        "device": device_count,
        "edge": edge_count,
        "fog": fog_count,
        "cloud": cloud_count,
    }
    if any(count < 0 for count in counts.values()):
        raise ValueError("Tier counts must be non-negative.")

    non_empty_tiers = [(name, count) for name, count in counts.items() if count > 0]
    total_nodes = sum(count for _, count in non_empty_tiers)
    if total_nodes == 0:
        raise ValueError("At least one tier must contain nodes.")

    if connectivity is None:
        connectivity = [1.0] * max(len(non_empty_tiers) - 1, 0)
    if cross_level_connectivity is None:
        cross_level_connectivity = [
            (
                0.0
                if name == "device"
                else 0.25
                if name == "edge"
                else 0.5
                if name == "fog"
                else 1.0
            )
            for name, _ in non_empty_tiers
        ]

    infrastructure = hierarchical(
        n=total_nodes,
        infrastructure_id=infrastructure_id,
        symmetric=symmetric,
        node_partitioning=[count / total_nodes for _, count in non_empty_tiers],
        connectivity=connectivity,
        cross_level_connectivity=cross_level_connectivity,
        update_policies=update_policies,
        node_assets=node_assets,
        link_assets=link_assets,
        include_default_assets=include_default_assets,
        strict=strict,
        resource_init=resource_init,
        placement_strategy=placement_strategy,
        path_algorithm=path_algorithm,
        seed=seed,
    )
    relabel_hierarchical_levels(
        infrastructure,
        [name for name, _ in non_empty_tiers],
    )

    tier_profiles = {
        "device": dict(
            cpu=1.0,
            gpu=0.0,
            ram=1.0,
            storage=1.0,
            availability=0.95,
            processing_time=8.0,
        ),
        "edge": dict(
            cpu=8.0,
            gpu=1.0,
            ram=16.0,
            storage=64.0,
            availability=0.98,
            processing_time=3.0,
        ),
        "fog": dict(
            cpu=16.0,
            gpu=2.0,
            ram=32.0,
            storage=256.0,
            availability=0.99,
            processing_time=2.0,
        ),
        "cloud": dict(
            cpu=32.0,
            gpu=4.0,
            ram=128.0,
            storage=1024.0,
            availability=0.999,
            processing_time=1.0,
        ),
    }
    for tier_name, _ in non_empty_tiers:
        profile = tier_node_assets(infrastructure, **tier_profiles[tier_name])
        for node_id in infrastructure.nodes:
            if node_id.startswith(f"{tier_name}_"):
                infrastructure.nodes[node_id].update(profile)

    return infrastructure
