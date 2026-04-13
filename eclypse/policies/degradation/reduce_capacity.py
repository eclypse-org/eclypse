"""Capacity degradation policy."""

from __future__ import annotations

from typing import TYPE_CHECKING

from eclypse.policies._filters import (
    ensure_numeric_value,
    iter_selected_edges,
    iter_selected_keys,
    iter_selected_nodes,
)

if TYPE_CHECKING:
    from eclypse.policies._filters import (
        EdgeFilter,
        NodeFilter,
    )
    from eclypse.utils.types import UpdatePolicy


def reduce_capacity(
    target_degradation: float,
    epochs: int,
    *,
    node_assets: list[str] | tuple[str, ...] | None = None,
    edge_assets: list[str] | tuple[str, ...] | None = None,
    node_ids: list[str] | None = None,
    node_filter: NodeFilter | None = None,
    edge_ids: list[tuple[str, str]] | None = None,
    edge_filter: EdgeFilter | None = None,
) -> UpdatePolicy:
    """Reduce selected capacities over a fixed number of epochs.

    Args:
        target_degradation (float): The target multiplicative degradation factor.
        epochs (int): The number of evolution steps over which to apply it.
        node_assets (list[str] | tuple[str, ...] | None): Node assets to degrade.
        edge_assets (list[str] | tuple[str, ...] | None): Edge assets to degrade.
        node_ids (list[str] | None): Optional explicit list of node ids to target.
        node_filter (NodeFilter | None): Optional predicate to filter target nodes.
        edge_ids (list[tuple[str, str]] | None): Optional explicit list of edges to
            target.
        edge_filter (EdgeFilter | None): Optional predicate to filter target edges.

    Returns:
        UpdatePolicy: A graph update policy reducing the selected assets.
    """
    _validate_epochs(epochs)
    if not 0 <= target_degradation <= 1:
        raise ValueError("target_degradation must be between 0 and 1.")

    step = 0
    factor = target_degradation ** (1 / epochs)

    def policy(graph):
        nonlocal step
        if step >= epochs:
            return

        for _, data in iter_selected_nodes(
            graph,
            node_ids=node_ids,
            node_filter=node_filter,
        ):
            for key in iter_selected_keys(data, node_assets):
                current = ensure_numeric_value(key, data[key])
                data[key] = current * factor

        for _, _, data in iter_selected_edges(
            graph,
            edge_ids=edge_ids,
            edge_filter=edge_filter,
        ):
            for key in iter_selected_keys(data, edge_assets):
                current = ensure_numeric_value(key, data[key])
                data[key] = current * factor

        step += 1

    return policy


def _validate_epochs(epochs: int):
    if epochs <= 0:
        raise ValueError("epochs must be strictly positive.")
