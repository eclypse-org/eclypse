"""Normalisation constraint policy."""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
)

from eclypse.policies._filters import (
    coerce_numeric_like,
    ensure_numeric_value,
    iter_selected_keys,
)

if TYPE_CHECKING:
    from eclypse.graph.asset_graph import AssetGraph
    from eclypse.utils.types import UpdatePolicy


def normalise(
    total: float,
    *,
    node_assets: str | list[str] | None = None,
    edge_assets: str | list[str] | None = None,
) -> UpdatePolicy:
    """Scale selected values so their graph-wide sum equals ``total``.

    Args:
        total (float): Desired sum across all selected assets.
        node_assets (str | list[str] | None): Optional node asset key selector.
        edge_assets (str | list[str] | None): Optional edge asset key selector.

    Returns:
        Policy that rescales selected numeric assets.
    """

    def policy(graph: AssetGraph):
        selected: list[tuple[dict[str, Any], str]] = []
        if node_assets is not None:
            for _, data in graph.nodes.data():
                selected.extend(
                    (data, key) for key in iter_selected_keys(data, node_assets)
                )
        if edge_assets is not None:
            for _, _, data in graph.edges.data():
                selected.extend(
                    (data, key) for key in iter_selected_keys(data, edge_assets)
                )
        current_total = 0.0
        for data, key in selected:
            current_total += ensure_numeric_value(key, data[key])
        if current_total == 0:
            return
        factor = total / current_total
        for data, key in selected:
            value = ensure_numeric_value(key, data[key]) * factor
            data[key] = coerce_numeric_like(data[key], value)

    return policy
