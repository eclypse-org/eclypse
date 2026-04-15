"""Momentum random walk policy."""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    TypeVar,
)

from eclypse.policies._filters import (
    clamp,
    iter_selected_edges,
    iter_selected_nodes,
)
from eclypse.policies.noise._helpers import (
    apply_additive_walk,
    validate_steps,
)

if TYPE_CHECKING:
    from eclypse.graph.asset_graph import AssetGraph
    from eclypse.policies._filters import (
        EdgeFilter,
        NodeFilter,
    )
    from eclypse.utils.types import UpdatePolicy


StateKeyT = TypeVar("StateKeyT", tuple[str, str], tuple[str, str, str])


def momentum_walk(
    *,
    node_steps: dict[str, float] | None = None,
    edge_steps: dict[str, float] | None = None,
    node_bounds: dict[str, tuple[float | None, float | None]] | None = None,
    edge_bounds: dict[str, tuple[float | None, float | None]] | None = None,
    momentum: float = 0.75,
    node_ids: list[str] | None = None,
    node_filter: NodeFilter | None = None,
    edge_ids: list[tuple[str, str]] | None = None,
    edge_filter: EdgeFilter | None = None,
) -> UpdatePolicy:
    """Apply additive random walks with directional persistence.

    Args:
        node_steps (dict[str, float] | None): Maximum additive step per node asset.
        edge_steps (dict[str, float] | None): Maximum additive step per edge asset.
        node_bounds (dict[str, tuple[float | None, float | None]] | None): Optional
            lower/upper bounds for node assets.
        edge_bounds (dict[str, tuple[float | None, float | None]] | None): Optional
            lower/upper bounds for edge assets.
        momentum (float): Fraction of the previous additive step reused at the
            next epoch. Must be between 0 and 1.
        node_ids (list[str] | None): Optional explicit list of node ids to target.
        node_filter (NodeFilter | None): Optional predicate to filter target nodes.
        edge_ids (list[tuple[str, str]] | None): Optional explicit list of target
            edges.
        edge_filter (EdgeFilter | None): Optional predicate to filter target edges.

    Returns:
        UpdatePolicy: A graph update policy applying momentum random walks.
    """
    validate_steps(node_steps=node_steps, edge_steps=edge_steps)

    if momentum < 0 or momentum > 1:
        raise ValueError("momentum must be between 0 and 1.")

    previous_node_deltas: dict[tuple[str, str], float] = {}
    previous_edge_deltas: dict[tuple[str, str, str], float] = {}

    def policy(graph: AssetGraph):
        for node_id, data in iter_selected_nodes(
            graph,
            node_ids=node_ids,
            node_filter=node_filter,
        ):
            apply_additive_walk(
                data,
                node_steps or {},
                node_bounds,
                delta_sampler=lambda key, step, node_id=node_id: _sample_momentum_delta(
                    previous_node_deltas,
                    (node_id, key),
                    step,
                    momentum=momentum,
                    random=graph.rnd,
                ),
            )

        for source, target, data in iter_selected_edges(
            graph,
            edge_ids=edge_ids,
            edge_filter=edge_filter,
        ):
            apply_additive_walk(
                data,
                edge_steps or {},
                edge_bounds,
                delta_sampler=lambda key, step, source=source, target=target: (
                    _sample_momentum_delta(
                        previous_edge_deltas,
                        (source, target, key),
                        step,
                        momentum=momentum,
                        random=graph.rnd,
                    )
                ),
            )

    return policy


def _sample_momentum_delta(
    previous_deltas: dict[StateKeyT, float],
    state_key: StateKeyT,
    step: float,
    *,
    momentum: float,
    random,
) -> float:
    """Sample a bounded additive delta with momentum from the previous epoch."""
    previous_delta = previous_deltas.get(state_key, 0.0)
    candidate = momentum * previous_delta + random.uniform(-step, step)
    delta = clamp(candidate, lower=-step, upper=step)
    previous_deltas[state_key] = delta
    return delta
