"""Synthetic backbone reference infrastructures.

The backbone family models synthetic long-haul backbones distributed through
TopoHub. These topologies emphasise WAN structure, geographic spread, and link
distance rather than node compute heterogeneity, making them a good reference
for routing, latency, and placement experiments over region-scale networks.

Example:
    .. code-block:: python

        get_backbone("africa", **kwargs)

Source:
    TopoHub, https://www.topohub.org
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from ._helpers import get_topohub

if TYPE_CHECKING:
    from collections.abc import Callable

    import networkx as nx

    from eclypse.graph import Infrastructure
    from eclypse.graph.assets import Asset
    from eclypse.utils.types import (
        InitPolicy,
        UpdatePolicies,
    )


def get_backbone(
    topology: str,
    infrastructure_id: str | None = None,
    update_policies: UpdatePolicies = None,
    node_assets: dict[str, Asset] | None = None,
    link_assets: dict[str, Asset] | None = None,
    include_default_assets: bool = False,
    resource_init: InitPolicy = "max",
    path_algorithm: Callable[[nx.Graph, str, str], list[str]] | None = None,
    seed: int | None = None,
) -> Infrastructure:
    """Create a synthetic backbone infrastructure from TopoHub.

    The ``topology`` value must be a valid topology name from
    `TopoHub <https://www.topohub.org>`_'s ``backbone`` family catalogue.

    Args:
        topology (str):
            Backbone topology identifier, such as ``"africa"``.
        infrastructure_id (str | None):
            Identifier assigned to the infrastructure. If omitted, a dataset-based
            identifier is used.
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
        seed (int | None):
            Seed forwarded to the infrastructure random generator.

    Returns:
        Infrastructure: The converted backbone infrastructure.
    """
    dataset_path = f"backbone/{topology}"
    return get_topohub(
        topology=dataset_path,
        infrastructure_id=infrastructure_id or f"backbone_{topology}",
        use_names=False,
        update_policies=update_policies,
        node_assets=node_assets,
        link_assets=link_assets,
        include_default_assets=include_default_assets,
        resource_init=resource_init,
        path_algorithm=path_algorithm,
        seed=seed,
    )


__all__ = ["get_backbone"]
