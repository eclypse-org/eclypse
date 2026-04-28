"""Random weighted policy composition."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from eclypse.graph.asset_graph import AssetGraph
    from eclypse.utils.types import UpdatePolicy


def weighted_choice(
    policies: list[UpdatePolicy] | tuple[UpdatePolicy, ...],
    weights: list[float] | tuple[float, ...],
) -> UpdatePolicy:
    """Run one policy sampled from explicit weights.

    Args:
        policies (list[UpdatePolicy] | tuple[UpdatePolicy, ...]): Candidate policies to sample from.
        weights (list[float] | tuple[float, ...]): Sampling weights aligned with ``policies``.

    Returns:
        Policy that calls one weighted-sampled child policy.
    """
    if len(policies) != len(weights):
        raise ValueError("weights must match policies length.")
    if any(weight < 0 for weight in weights):
        raise ValueError("weights must be non-negative.")
    if sum(weights) <= 0:
        raise ValueError("at least one weight must be positive.")

    def policy(graph: AssetGraph):
        graph.rnd.choices(policies, weights=weights, k=1)[0](graph)

    return policy
