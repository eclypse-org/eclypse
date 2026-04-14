"""Impulse noise policy."""

from __future__ import annotations

from typing import TYPE_CHECKING

from eclypse.policies._filters import (
    iter_selected_edges,
    iter_selected_nodes,
)
from eclypse.policies.noise._helpers import (
    apply_impulses,
    validate_factor_range,
    validate_probability,
)
from eclypse.utils.constants import MIN_FLOAT

if TYPE_CHECKING:
    from eclypse.policies._filters import (
        EdgeFilter,
        NodeFilter,
    )
    from eclypse.utils.types import UpdatePolicy


def impulse(
    *,
    node_assets: str | list[str] | None = None,
    edge_assets: str | list[str] | None = None,
    probability: float = 0.05,
    node_factor_range: tuple[float, float] = (0.5, 1.5),
    edge_factor_range: tuple[float, float] | None = None,
    minimum: float = MIN_FLOAT,
    node_ids: list[str] | None = None,
    node_filter: NodeFilter | None = None,
    edge_ids: list[tuple[str, str]] | None = None,
    edge_filter: EdgeFilter | None = None,
) -> UpdatePolicy:
    """Apply rare multiplicative shocks to selected node and edge assets.

    Args:
        node_assets (str | list[str] | None): Node assets eligible for impulses.
        edge_assets (str | list[str] | None): Edge assets eligible for impulses.
        probability (float): Per-asset probability of an impulse at each epoch.
        node_factor_range (tuple[float, float]): Multiplicative factor range used
            for shocked node assets.
        edge_factor_range (tuple[float, float] | None): Multiplicative factor
            range used for shocked edge assets. Defaults to ``node_factor_range``.
        minimum (float): Lower clamp applied after a shock.
        node_ids (list[str] | None): Optional explicit list of node ids to target.
        node_filter (NodeFilter | None): Optional predicate to filter target nodes.
        edge_ids (list[tuple[str, str]] | None): Optional explicit list of target
            edges.
        edge_filter (EdgeFilter | None): Optional predicate to filter target edges.

    Returns:
        UpdatePolicy: A graph update policy applying rare multiplicative shocks.
    """
    if node_assets is None and edge_assets is None:
        raise ValueError("At least one of node_assets or edge_assets must be provided.")

    validate_probability("probability", probability)
    validate_factor_range("node_factor_range", node_factor_range)

    effective_edge_factor_range = (
        node_factor_range if edge_factor_range is None else edge_factor_range
    )
    validate_factor_range("edge_factor_range", effective_edge_factor_range)

    def policy(graph):
        for _, data in iter_selected_nodes(
            graph,
            node_ids=node_ids,
            node_filter=node_filter,
        ):
            apply_impulses(
                data,
                node_assets,
                probability=probability,
                factor_range=node_factor_range,
                minimum=minimum,
                random=graph.rnd,
            )

        for _, _, data in iter_selected_edges(
            graph,
            edge_ids=edge_ids,
            edge_filter=edge_filter,
        ):
            apply_impulses(
                data,
                edge_assets,
                probability=probability,
                factor_range=effective_edge_factor_range,
                minimum=minimum,
                random=graph.rnd,
            )

    return policy
