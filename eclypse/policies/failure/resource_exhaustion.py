"""Resource exhaustion policy."""

from __future__ import annotations

from typing import TYPE_CHECKING

from eclypse.policies._filters import (
    NO_CHANGE,
    apply_numeric_transform,
    clamp,
)
from eclypse.policies._helpers import validate_probability

if TYPE_CHECKING:
    from eclypse.graph.asset_graph import AssetGraph
    from eclypse.policies._filters import (
        EdgeFilter,
        NodeFilter,
        NumericTransformResult,
    )
    from eclypse.utils.types import (
        NumericBasis,
        UpdatePolicy,
    )


def resource_exhaustion(
    probability: float = 1.0,
    *,
    factor: float = 0.5,
    minimum: float = 0.0,
    node_assets: str | list[str] | None = None,
    edge_assets: str | list[str] | None = None,
    node_ids: list[str] | None = None,
    node_filter: NodeFilter | None = None,
    edge_ids: list[tuple[str, str]] | None = None,
    edge_filter: EdgeFilter | None = None,
    basis: NumericBasis = "current",
) -> UpdatePolicy:
    """Reduce selected capacity-like assets according to ``factor``.

    Args:
        probability (float): Per-asset probability of applying the reduction.
        factor (float): Multiplicative reduction factor.
        minimum (float): Lower bound after reduction.
        node_assets (str | list[str] | None): Optional node asset key selector.
        edge_assets (str | list[str] | None): Optional edge asset key selector.
        node_ids (list[str] | None): Optional explicit node identifiers to mutate.
        node_filter (NodeFilter | None):
            Optional predicate receiving ``(node_id, data)``.
        edge_ids (list[tuple[str, str]] | None):
            Optional explicit edge identifiers to mutate.
        edge_filter (EdgeFilter | None):
            Optional predicate receiving ``(source, target, data)``.
        basis (NumericBasis):
            ``"current"`` compounds reductions. ``"initial"`` reduces the first
            value seen by this policy.

    Returns:
        Policy that reduces selected numeric assets.
    """
    validate_probability("probability", probability)
    if factor < 0:
        raise ValueError("factor must be non-negative.")
    if node_assets is None and edge_assets is None:
        raise ValueError("At least one of node_assets or edge_assets must be provided.")

    baselines: dict[tuple[str, ...], float] = {}

    def policy(graph: AssetGraph):
        def transform(_key: str, current: float) -> NumericTransformResult:
            if graph.rnd.random() >= probability:
                return NO_CHANGE
            return clamp(current * factor, lower=minimum)

        apply_numeric_transform(
            graph,
            node_assets=node_assets,
            edge_assets=edge_assets,
            node_ids=node_ids,
            node_filter=node_filter,
            edge_ids=edge_ids,
            edge_filter=edge_filter,
            transform=transform,
            basis=basis,
            baselines=baselines if basis == "initial" else None,
        )

        graph.logger.trace("Applied resource_exhaustion policy.")

    return policy
