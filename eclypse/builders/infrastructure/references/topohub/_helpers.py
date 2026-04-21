"""Helper functions shared by TopoHub-backed infrastructure references."""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
)

import networkx as nx

from eclypse.builders._helpers import prune_assets
from eclypse.graph import Infrastructure
from eclypse.simulation.config import _require_module

if TYPE_CHECKING:
    from collections.abc import Callable

    from eclypse.graph.assets import Asset
    from eclypse.placement.strategies import PlacementStrategy
    from eclypse.utils.types import (
        InitPolicy,
        UpdatePolicies,
    )


def get_topohub(
    topology: str,
    use_names: bool = False,
    infrastructure_id: str | None = None,
    update_policies: UpdatePolicies = None,
    node_assets: dict[str, Asset] | None = None,
    link_assets: dict[str, Asset] | None = None,
    include_default_assets: bool = False,
    resource_init: InitPolicy = "max",
    path_algorithm: Callable[[nx.Graph, str, str], list[str]] | None = None,
    placement_strategy: PlacementStrategy | None = None,
    seed: int | None = None,
) -> Infrastructure:
    """Create an infrastructure from any TopoHub topology path.

    The ``topology`` value must be a valid TopoHub dataset path. Available paths
    can be inspected from the TopoHub repository catalogue and documentation.

    Args:
        topology (str):
            Full TopoHub topology path, such as ``"sndlib/polska"``,
            ``"topozoo/Abilene"``, or ``"gabriel/25/0"``.
        use_names (bool):
            Whether TopoHub should use node names as node identifiers.
        infrastructure_id (str | None):
            Identifier assigned to the infrastructure. If omitted, a dataset-based
            identifier is derived from the topology path.
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
        Infrastructure: The converted TopoHub infrastructure.
    """
    _require_module("topohub")

    import topohub  # type: ignore[import-not-found,import-untyped]

    topo = topohub.get(topology, use_names=use_names)
    graph = nx.node_link_graph(topo, edges="edges")
    default_id = topology.replace("/", "_").replace("-", "_")
    infrastructure = Infrastructure(
        infrastructure_id=infrastructure_id or default_id,
        update_policies=update_policies,
        node_assets=node_assets,
        edge_assets=link_assets,
        include_default_assets=include_default_assets,
        resource_init=resource_init,
        path_algorithm=path_algorithm,
        placement_strategy=placement_strategy,
        seed=seed,
    )

    _copy_graph_metadata(infrastructure, graph, topology)

    node_mapping = {
        node_id: _normalise_node_id(node_id, data, use_names=use_names)
        for node_id, data in graph.nodes(data=True)
    }

    for source_id, attrs in graph.nodes(data=True):
        node_id = node_mapping[source_id]
        metadata = _node_metadata(attrs, use_names=use_names)
        metadata.setdefault("topohub_id", source_id)
        infrastructure.add_node(
            node_id,
            strict=False,
            **metadata,
        )

    for source_id, target_id, attrs in graph.edges(data=True):
        source = node_mapping[source_id]
        target = node_mapping[target_id]
        edge_attrs = _edge_attributes(infrastructure, attrs)
        edge_attrs.update(
            {key: value for key, value in attrs.items() if key not in edge_attrs}
        )
        infrastructure.add_edge(
            source,
            target,
            symmetric=True,
            strict=False,
            **edge_attrs,
        )

    return infrastructure


def _copy_graph_metadata(
    infrastructure: Infrastructure,
    graph: nx.Graph,
    dataset_path: str,
) -> None:
    """Copy graph-level metadata from TopoHub into the infrastructure."""
    infrastructure.graph.update(graph.graph)
    infrastructure.graph["dataset_path"] = dataset_path


def _normalise_node_id(
    node_id: Any,
    attrs: dict[str, Any],
    use_names: bool,
) -> str:
    """Return a stable string node identifier for ECLYPSE."""
    if use_names and isinstance(attrs.get("name"), str) and attrs["name"]:
        return attrs["name"]
    if isinstance(node_id, str):
        return node_id
    if isinstance(attrs.get("name"), str) and attrs["name"] and not use_names:
        return f"n{node_id}"
    return f"n{node_id}"


def _node_metadata(
    attrs: dict[str, Any],
    use_names: bool,
) -> dict[str, Any]:
    """Return node metadata according to the selected identifier policy."""
    metadata = dict(attrs)
    if use_names:
        metadata.pop("name", None)
    return metadata


def _edge_attributes(
    infrastructure: Infrastructure,
    attrs: dict[str, Any],
) -> dict[str, Any]:
    """Map TopoHub edge metadata into ECLYPSE edge assets."""
    edge_assets: dict[str, Any] = {}

    latency = next(
        (
            float(attrs[key])
            for key in ("latency", "delay")
            if isinstance(attrs.get(key), (int, float))
        ),
        None,
    )
    if latency is None and isinstance(attrs.get("dist"), (int, float)):
        latency = float(attrs["dist"]) / 200.0

    if latency is not None:
        edge_assets.update(
            prune_assets(
                infrastructure.edge_assets,
                latency=latency,
            )
        )

    for key in (
        "bandwidth",
        "capacity",
        "preinstalled_capacity",
        "preinstalled_cap",
    ):
        value = attrs.get(key)
        if isinstance(value, (int, float)):
            edge_assets.update(
                prune_assets(
                    infrastructure.edge_assets,
                    bandwidth=float(value),
                )
            )
            break

    return edge_assets


__all__ = ["get_topohub"]
