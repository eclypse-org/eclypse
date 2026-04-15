"""Run a policy from a given step onward."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from eclypse.graph.asset_graph import AssetGraph
    from eclypse.utils.types import UpdatePolicy


@dataclass(slots=True)
class AfterPolicy:
    """Run a policy from ``start`` onward."""

    start: int
    policy: UpdatePolicy
    step: int = 0

    def __post_init__(self):
        """Validate the schedule configuration."""
        if self.start < 0:
            raise ValueError("start must be non-negative.")

    def __call__(self, graph: AssetGraph):
        """Apply the wrapped policy from the configured step onward."""
        if self.step >= self.start:
            self.policy(graph)
        self.step += 1


def after(
    start: int,
    policy: UpdatePolicy,
) -> UpdatePolicy:
    """Run a policy from ``start`` onward.

    Args:
        start (int): First step at which the policy should run.
        policy (UpdatePolicy): The wrapped policy.

    Returns:
        UpdatePolicy: A scheduled wrapper around ``policy``.
    """
    return AfterPolicy(start=start, policy=policy)
