"""Bounded random walk policy."""

from __future__ import annotations

from typing import TYPE_CHECKING

from eclypse.policies._filters import (
    clamp,
    coerce_numeric_like,
    ensure_numeric_value,
    iter_selected_edges,
    iter_selected_nodes,
)

if TYPE_CHECKING:
    from eclypse.policies._filters import (
        EdgeFilter,
        NodeFilter,
    )
    from eclypse.utils.types import UpdatePolicy


def bounded_random_walk(
    *,
    node_steps: dict[str, float] | None = None,
    edge_steps: dict[str, float] | None = None,
    node_bounds: dict[str, tuple[float | None, float | None]] | None = None,
    edge_bounds: dict[str, tuple[float | None, float | None]] | None = None,
    node_ids: list[str] | None = None,
    node_filter: NodeFilter | None = None,
    edge_ids: list[tuple[str, str]] | None = None,
    edge_filter: EdgeFilter | None = None,
) -> UpdatePolicy:
    """Apply additive random walks while clamping values within bounds.

    Args:
        node_steps (dict[str, float] | None): Maximum additive step per node asset.
        edge_steps (dict[str, float] | None): Maximum additive step per edge asset.
        node_bounds (dict[str, tuple[float | None, float | None]] | None): Optional
            lower/upper bounds for node assets.
        edge_bounds (dict[str, tuple[float | None, float | None]] | None): Optional
            lower/upper bounds for edge assets.
        node_ids (list[str] | None): Optional explicit list of node ids to target.
        node_filter (NodeFilter | None): Optional predicate to filter target nodes.
        edge_ids (list[tuple[str, str]] | None): Optional explicit list of target
            edges.
        edge_filter (EdgeFilter | None): Optional predicate to filter target edges.

    Returns:
        UpdatePolicy: A graph update policy applying bounded random walks.
    """
    if not node_steps and not edge_steps:
        raise ValueError("At least one of node_steps or edge_steps must be provided.")

    for key, step in (node_steps or {}).items():
        if step < 0:
            raise ValueError(f'node step for "{key}" must be non-negative.')

    for key, step in (edge_steps or {}).items():
        if step < 0:
            raise ValueError(f'edge step for "{key}" must be non-negative.')

    def policy(graph):
        for _, data in iter_selected_nodes(
            graph,
            node_ids=node_ids,
            node_filter=node_filter,
        ):
            _apply_random_walk_to_values(
                data,
                node_steps or {},
                node_bounds,
                random=graph.rnd,
            )

        for _, _, data in iter_selected_edges(
            graph,
            edge_ids=edge_ids,
            edge_filter=edge_filter,
        ):
            _apply_random_walk_to_values(
                data,
                edge_steps or {},
                edge_bounds,
                random=graph.rnd,
            )

    return policy


def _apply_random_walk_to_values(
    values: dict[str, object],
    steps: dict[str, float],
    bounds: dict[str, tuple[float | None, float | None]] | None,
    *,
    random,
):
    for key, step in steps.items():
        if key not in values:
            continue
        current = ensure_numeric_value(key, values[key])
        lower, upper = (bounds or {}).get(key, (0.0, None))
        delta = random.uniform(-step, step)
        values[key] = coerce_numeric_like(
            values[key],
            clamp(current + delta, lower=lower, upper=upper),
        )
