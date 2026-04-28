"""Gaussian additive jitter noise policy."""

from __future__ import annotations

from typing import TYPE_CHECKING

from eclypse.policies._filters import (
    apply_numeric_transform,
    clamp,
)

if TYPE_CHECKING:
    from eclypse.graph.asset_graph import AssetGraph
    from eclypse.policies._filters import (
        EdgeFilter,
        NodeFilter,
    )
    from eclypse.utils.types import UpdatePolicy


def gaussian_jitter(
    *,
    node_parameters: dict[str, tuple[float, float]] | None = None,
    edge_parameters: dict[str, tuple[float, float]] | None = None,
    lower: float | None = None,
    upper: float | None = None,
    node_ids: list[str] | None = None,
    node_filter: NodeFilter | None = None,
    edge_ids: list[tuple[str, str]] | None = None,
    edge_filter: EdgeFilter | None = None,
) -> UpdatePolicy:
    """Add Gaussian sampled deltas to selected assets.

    Args:
        node_parameters (dict[str, tuple[float, float]] | None):
            Mapping from node asset name to ``(mean, std)``.
        edge_parameters (dict[str, tuple[float, float]] | None):
            Mapping from edge asset name to ``(mean, std)``.
        lower (float | None): Optional lower bound after adding noise.
        upper (float | None): Optional upper bound after adding noise.
        node_ids (list[str] | None): Optional explicit node identifiers to mutate.
        node_filter (NodeFilter | None): Optional predicate receiving ``(node_id, data)``.
        edge_ids (list[tuple[str, str]] | None): Optional explicit edge identifiers to mutate.
        edge_filter (EdgeFilter | None): Optional predicate receiving ``(source, target, data)``.

    Returns:
        Policy that adds independent Gaussian jitter to selected assets.
    """
    _validate_parameters(node_parameters, edge_parameters)

    def policy(graph: AssetGraph):
        def node_transform(key: str, current: float) -> float:
            mean, std = (node_parameters or {})[key]
            return clamp(current + graph.rnd.gauss(mean, std), lower, upper)

        def edge_transform(key: str, current: float) -> float:
            mean, std = (edge_parameters or {})[key]
            return clamp(current + graph.rnd.gauss(mean, std), lower, upper)

        apply_numeric_transform(
            graph,
            node_assets=list(node_parameters or {}),
            node_ids=node_ids,
            node_filter=node_filter,
            transform=node_transform,
        )
        apply_numeric_transform(
            graph,
            edge_assets=list(edge_parameters or {}),
            edge_ids=edge_ids,
            edge_filter=edge_filter,
            transform=edge_transform,
        )

        graph.logger.trace("Applied gaussian_jitter policy.")

    return policy


def _validate_parameters(*parameter_sets):
    if all(not parameter_set for parameter_set in parameter_sets):
        raise ValueError("At least one parameter mapping must be provided.")
    for parameter_set in parameter_sets:
        for _, std in (parameter_set or {}).values():
            if std < 0:
                raise ValueError("standard deviation must be non-negative.")
