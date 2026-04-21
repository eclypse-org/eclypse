"""Helper functions shared by infrastructure builders."""

from __future__ import annotations

from typing import TYPE_CHECKING

import networkx as nx

from eclypse.builders._helpers import prune_assets

if TYPE_CHECKING:
    from typing import Any

    from eclypse.graph import Infrastructure


def add_nodes(
    infrastructure: Infrastructure,
    node_ids: list[str],
    strict: bool = False,
    **assets: Any,
) -> None:
    """Add a batch of nodes with the same asset values.

    Args:
        infrastructure (Infrastructure):
            Infrastructure receiving the nodes.
        node_ids (list[str]):
            Node identifiers to add.
        strict (bool):
            Whether inconsistent asset values should raise.
        **assets:
            Concrete node asset values applied to every node.
    """
    for node_id in node_ids:
        infrastructure.add_node(node_id, strict=strict, **assets)


def connect_pairs(
    infrastructure: Infrastructure,
    pairs: list[tuple[str, str]],
    symmetric: bool = False,
    strict: bool = False,
    **assets: Any,
) -> None:
    """Add links described as explicit source-target pairs.

    Args:
        infrastructure (Infrastructure):
            Infrastructure receiving the links.
        pairs (list[tuple[str, str]]):
            Ordered source-target pairs to connect.
        symmetric (bool):
            Whether to mirror each link in the opposite direction.
        strict (bool):
            Whether inconsistent asset values should raise.
        **assets:
            Concrete edge asset values applied to every link.
    """
    for source, target in pairs:
        infrastructure.add_edge(
            source,
            target,
            symmetric=symmetric,
            strict=strict,
            **assets,
        )


def connect_round_robin(
    infrastructure: Infrastructure,
    sources: list[str],
    targets: list[str],
    symmetric: bool = False,
    strict: bool = False,
    **assets: Any,
) -> None:
    """Connect each source to a target chosen in round-robin order.

    Args:
        infrastructure (Infrastructure):
            Infrastructure receiving the links.
        sources (list[str]):
            Source node identifiers.
        targets (list[str]):
            Target node identifiers.
        symmetric (bool):
            Whether to mirror each link in the opposite direction.
        strict (bool):
            Whether inconsistent asset values should raise.
        **assets:
            Concrete edge asset values applied to every link.

    Raises:
        ValueError: If ``targets`` is empty.
    """
    if not targets:
        raise ValueError("At least one target node is required.")

    for index, source in enumerate(sources):
        infrastructure.add_edge(
            source,
            targets[index % len(targets)],
            symmetric=symmetric,
            strict=strict,
            **assets,
        )


def connect_clique(
    infrastructure: Infrastructure,
    node_ids: list[str],
    symmetric: bool = True,
    strict: bool = False,
    **assets: Any,
) -> None:
    """Connect every distinct pair of nodes in the provided group.

    Args:
        infrastructure (Infrastructure):
            Infrastructure receiving the links.
        node_ids (list[str]):
            Node identifiers to connect as a clique.
        symmetric (bool):
            Whether to mirror each link in the opposite direction.
        strict (bool):
            Whether inconsistent asset values should raise.
        **assets:
            Concrete edge asset values applied to every link.
    """
    pairs = [
        (node_ids[i], node_ids[j])
        for i in range(len(node_ids))
        for j in range(i + 1, len(node_ids))
    ]
    connect_pairs(
        infrastructure,
        pairs,
        symmetric=symmetric,
        strict=strict,
        **assets,
    )


def relabel_hierarchical_levels(
    infrastructure: Infrastructure,
    level_prefixes: list[str],
) -> Infrastructure:
    """Rename ``hierarchical`` level nodes using semantic tier prefixes.

    Args:
        infrastructure (Infrastructure):
            Infrastructure returned by the hierarchical generator.
        level_prefixes (list[str]):
            Semantic prefix for each hierarchy level in order.

    Returns:
        Infrastructure: The relabelled infrastructure.
    """
    mapping: dict[str, str] = {}
    for node_id in list(infrastructure.nodes):
        level, index = node_id.split("_", maxsplit=1)
        prefix = level_prefixes[int(level[1:])]
        mapping[node_id] = f"{prefix}_{index}"

    nx.relabel_nodes(infrastructure, mapping, copy=False)
    infrastructure._invalidate_cache()  # pylint: disable=protected-access
    return infrastructure


def tier_node_assets(
    infrastructure: Infrastructure,
    **asset_values: Any,
) -> dict[str, Any]:
    """Return only the node assets supported by the infrastructure.

    Args:
        infrastructure (Infrastructure):
            Infrastructure whose node asset bucket is inspected.
        **asset_values:
            Candidate asset values.

    Returns:
        dict[str, Any]: Asset values supported by the infrastructure.
    """
    return prune_assets(infrastructure.node_assets, **asset_values)


def tier_link_assets(
    infrastructure: Infrastructure,
    **asset_values: Any,
) -> dict[str, Any]:
    """Return only the edge assets supported by the infrastructure.

    Args:
        infrastructure (Infrastructure):
            Infrastructure whose edge asset bucket is inspected.
        **asset_values:
            Candidate asset values.

    Returns:
        dict[str, Any]: Asset values supported by the infrastructure.
    """
    return prune_assets(infrastructure.edge_assets, **asset_values)


__all__ = [
    "add_nodes",
    "connect_clique",
    "connect_pairs",
    "connect_round_robin",
    "relabel_hierarchical_levels",
    "tier_link_assets",
    "tier_node_assets",
]
