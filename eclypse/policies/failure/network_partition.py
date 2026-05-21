"""Network partition policy."""

from __future__ import annotations

from typing import TYPE_CHECKING

from eclypse.utils.constants import MIN_AVAILABILITY

_MIN_PARTITIONS = 2

if TYPE_CHECKING:
    from eclypse.graph.asset_graph import AssetGraph
    from eclypse.utils.types import UpdatePolicy


def network_partition(
    groups: list[list[str]],
    *,
    availability_key: str = "availability",
    unavailable_value: float = MIN_AVAILABILITY,
    remove_edges: bool = False,
) -> UpdatePolicy:
    """Partition node groups by disabling or removing cross-group edges.

    Args:
        groups (list[list[str]]): Node identifiers grouped by partition.
        availability_key (str): Edge asset used when cross-group edges are disabled.
        unavailable_value (float): Value written to disabled cross-group edges.
        remove_edges (bool):
            Whether to remove cross-group edges instead of mutating them.

    Returns:
        Policy that isolates the configured partitions.
    """
    if len(groups) < _MIN_PARTITIONS:
        raise ValueError("groups must contain at least two partitions.")
    node_to_group = {
        node_id: group_idx
        for group_idx, group in enumerate(groups)
        for node_id in group
    }

    def policy(graph: AssetGraph):
        for source, target, data in list(graph.edges.data()):
            source_group = node_to_group.get(source)
            target_group = node_to_group.get(target)
            if (
                source_group is None
                or target_group is None
                or source_group == target_group
            ):
                continue
            if remove_edges:
                graph.remove_edge(source, target)
            else:
                data[availability_key] = unavailable_value

        graph.logger.trace("Applied network_partition policy.")

    return policy
