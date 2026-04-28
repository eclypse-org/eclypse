"""Traffic matrix workload policy."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from eclypse.graph.asset_graph import AssetGraph
    from eclypse.utils.types import UpdatePolicy


def traffic_matrix(
    matrix: dict[tuple[str, str], float],
    *,
    asset: str = "traffic",
    additive: bool = False,
) -> UpdatePolicy:
    """Apply edge traffic values from a source-target matrix.

    Args:
        matrix (dict[tuple[str, str], float]):
            Mapping from ``(source, target)`` edge id to traffic value.
        asset (str): Edge asset written by the policy.
        additive (bool): Whether to add to existing traffic instead of replacing it.

    Returns:
        Policy that writes traffic values onto matching edges.
    """

    def policy(graph: AssetGraph):
        for edge_id, value in matrix.items():
            if not graph.has_edge(*edge_id):
                continue
            if additive:
                graph.edges[edge_id][asset] = graph.edges[edge_id].get(asset, 0) + value
            else:
                graph.edges[edge_id][asset] = value

    return policy
