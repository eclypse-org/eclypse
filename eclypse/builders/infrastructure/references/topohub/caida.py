"""CAIDA-backed reference infrastructures.

The CAIDA family models Internet-scale AS connectivity snapshots processed by
TopoHub from CAIDA Ark data. These references focus on large-scale structural
properties and peering relationships rather than node compute capabilities, so
ECLYPSE keeps node resources implicit and relies on the infrastructure
initialisation policy for unspecified assets.

Example:
    .. code-block:: python

        get_caida("2024-01", **kwargs)

Source:
    CAIDA Ark, https://www.caida.org/catalog/datasets/ark/
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


def get_caida(
    snapshot: str,
    infrastructure_id: str | None = None,
    update_policies: UpdatePolicies = None,
    node_assets: dict[str, Asset] | None = None,
    link_assets: dict[str, Asset] | None = None,
    include_default_assets: bool = False,
    resource_init: InitPolicy = "max",
    path_algorithm: Callable[[nx.Graph, str, str], list[str]] | None = None,
    seed: int | None = None,
) -> Infrastructure:
    """Create a CAIDA-backed infrastructure from TopoHub.

    The ``snapshot`` value must be a valid topology name from
    `TopoHub <https://www.topohub.org>`_'s ``caida`` family catalogue.

    Args:
        snapshot (str):
            CAIDA snapshot identifier within TopoHub.
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
        Infrastructure: The converted CAIDA infrastructure.
    """
    dataset_path = f"caida/{snapshot}"
    return get_topohub(
        topology=dataset_path,
        infrastructure_id=infrastructure_id or f"caida_{snapshot}",
        use_names=False,
        update_policies=update_policies,
        node_assets=node_assets,
        link_assets=link_assets,
        include_default_assets=include_default_assets,
        resource_init=resource_init,
        path_algorithm=path_algorithm,
        seed=seed,
    )


__all__ = ["get_caida"]
