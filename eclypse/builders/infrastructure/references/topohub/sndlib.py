"""SNDlib-backed reference infrastructures.

The SNDlib family models published backbone and traffic-engineering benchmark
topologies from the Survivable Network Design Library. These references provide
realistic inter-site connectivity, geographic link lengths, and traffic-related
metadata such as demand matrices and ECMP load statistics when present in
TopoHub.

Example:
    .. code-block:: python

        get_sndlib("polska", **kwargs)

Source:
    SNDlib, https://sndlib.put.poznan.pl/
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


def get_sndlib(
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
    """Create a SNDlib-backed infrastructure from TopoHub.

    The ``topology`` value must be a valid topology name from
    `TopoHub <https://www.topohub.org>`_'s ``sndlib`` family catalogue.

    Args:
        topology (str):
            SNDlib topology identifier, such as ``"polska"`` or ``"geant"``.
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
        Infrastructure: The converted SNDlib infrastructure.
    """
    dataset_path = f"sndlib/{topology}"
    return get_topohub(
        topology=dataset_path,
        infrastructure_id=infrastructure_id or f"sndlib_{topology}",
        use_names=True,
        update_policies=update_policies,
        node_assets=node_assets,
        link_assets=link_assets,
        include_default_assets=include_default_assets,
        resource_init=resource_init,
        path_algorithm=path_algorithm,
        seed=seed,
    )


__all__ = ["get_sndlib"]
