"""Reference topology for the Orion Crew Exploration Vehicle network.

The Orion Crew Exploration Vehicle (CEV) reference models a published mixed-criticality
embedded network with end systems and switching nodes. The topology includes
multiple layers of avionics switches, distributed units, controllers, and
mission subsystems, all connected through a fixed embedded communication
backbone.

Its featured capabilities are those of a structured mixed-criticality network:
deterministic switch-centric connectivity, explicit separation between end
systems and network switches, and link/node resources suitable for analysing QoS
constraints such as latency, bandwidth, and availability in a safety-oriented
setting.

Source:
    Berisa et al., "AVB-aware Routing and Scheduling for Critical Traffic in
    Time-sensitive Networks with Preemption", RTNS 2022,
    https://dl.acm.org/doi/10.1145/3534879.3534926
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from eclypse.builders._helpers import prune_assets
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


def get_orion_cev(
    infrastructure_id: str = "orion_cev",
    update_policies: UpdatePolicies = None,
    node_assets: dict[str, Asset] | None = None,
    link_assets: dict[str, Asset] | None = None,
    include_default_assets: bool = False,
    resource_init: InitPolicy = "max",
    path_algorithm: Callable[[nx.Graph, str, str], list[str]] | None = None,
    placement_strategy: PlacementStrategy | None = None,
    seed: int | None = None,
) -> Infrastructure:
    """Create the Orion CEV reference infrastructure.

    Args:
        infrastructure_id (str):
            Identifier assigned to the infrastructure.
        update_policies (UpdatePolicies):
            Graph update policies executed during ``evolve()``.
        node_assets (dict[str, Asset] | None):
            Node asset definitions available to the infrastructure.
        link_assets (dict[str, Asset] | None):
            Edge asset definitions available to the infrastructure.
        include_default_assets (bool):
            Whether to include default ECLYPSE assets.
        resource_init (InitPolicy):
            Initialisation policy used for graph assets.
        path_algorithm (Callable[[nx.Graph, str, str], list[str]] | None):
            Path computation function for infrastructure routing.
        placement_strategy (PlacementStrategy | None):
            Optional placement strategy attached to the infrastructure.
        seed (int | None):
            Seed forwarded to the infrastructure random generator.

    Returns:
        Infrastructure: The Orion CEV infrastructure.
    """
    infra = Infrastructure(
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

    end_systems = [
        "DU11",
        "DU12",
        "DU13",
        "DU21",
        "DU22",
        "FCM1",
        "LCM1",
        "RCM1",
        "CM1CA",
        "CM1CB",
        "FCM2",
        "LCM2",
        "RCM2",
        "CM2CA",
        "CM2CB",
        "CMRIU1",
        "CMRIU2",
        "BFCU",
        "SBAND1",
        "SBAND2",
        "MIMU1",
        "MIMU2",
        "MIMU3",
        "StarTr1",
        "StarTr2",
        "SM1CA",
        "SM1CB",
        "SMRIU1",
        "SMRIU2",
        "SM2CA",
        "SM2CB",
    ]
    network_switches = [
        "NS11",
        "NS12",
        "NS13",
        "NS14",
        "NS21",
        "NS22",
        "NS31",
        "NS32",
        "NS41",
        "NS42",
        "NS51",
        "NS52",
        "NS6",
        "NS7",
        "NS8",
    ]

    for es in end_systems:
        infra.add_node(
            es,
            **prune_assets(
                infra.node_assets,
                cpu=1.0,
                gpu=0,
                ram=1.0,
                storage=0.5,
                availability=0.98,
                processing_time=10,
            ),
        )
    for ns in network_switches:
        infra.add_node(
            ns,
            **prune_assets(
                infra.node_assets,
                cpu=0.5,
                gpu=0,
                ram=0.25,
                storage=0.2,
                availability=0.995,
                processing_time=1,
            ),
        )

    edges = [
        ("DU11", "NS11"),
        ("DU12", "NS11"),
        ("DU13", "NS11"),
        ("DU21", "NS14"),
        ("DU22", "NS14"),
        ("SBAND1", "NS12"),
        ("SBAND2", "NS12"),
        ("MIMU1", "NS13"),
        ("MIMU2", "NS13"),
        ("MIMU3", "NS13"),
        ("StarTr1", "NS13"),
        ("StarTr2", "NS13"),
        ("CMRIU1", "NS21"),
        ("CMRIU2", "NS22"),
        ("BFCU", "NS22"),
        ("FCM1", "NS31"),
        ("LCM1", "NS31"),
        ("RCM1", "NS31"),
        ("FCM2", "NS32"),
        ("LCM2", "NS32"),
        ("RCM2", "NS32"),
        ("CM1CA", "NS41"),
        ("CM1CB", "NS41"),
        ("SM1CA", "NS51"),
        ("SM1CB", "NS51"),
        ("SMRIU1", "NS6"),
        ("SMRIU2", "NS6"),
        ("CM2CA", "NS42"),
        ("CM2CB", "NS42"),
        ("SM2CA", "NS52"),
        ("SM2CB", "NS52"),
        ("NS11", "NS21"),
        ("NS11", "NS22"),
        ("NS12", "NS21"),
        ("NS12", "NS22"),
        ("NS13", "NS21"),
        ("NS13", "NS22"),
        ("NS14", "NS21"),
        ("NS14", "NS22"),
        ("NS21", "NS7"),
        ("NS21", "NS31"),
        ("NS22", "NS7"),
        ("NS22", "NS32"),
        ("NS7", "NS31"),
        ("NS7", "NS32"),
        ("NS31", "NS41"),
        ("NS31", "NS6"),
        ("NS31", "NS8"),
        ("NS32", "NS42"),
        ("NS32", "NS6"),
        ("NS32", "NS8"),
        ("NS41", "NS51"),
        ("NS42", "NS52"),
        ("NS8", "NS51"),
        ("NS8", "NS52"),
    ]
    for source, target in edges:
        infra.add_edge(
            source,
            target,
            symmetric=True,
            **prune_assets(infra.edge_assets, latency=10, bandwidth=100),
        )
    return infra
