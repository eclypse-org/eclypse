"""Run a policy at a fixed interval."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from eclypse.graph.asset_graph import AssetGraph
    from eclypse.utils.types import UpdatePolicy


@dataclass(slots=True)
class EveryPolicy:
    """Run a policy every ``interval`` steps starting from ``start``."""

    interval: int
    policy: UpdatePolicy
    start: int = 0
    step: int = 0

    def __post_init__(self):
        """Validate the schedule configuration."""
        if self.interval <= 0:
            raise ValueError("interval must be strictly positive.")
        if self.start < 0:
            raise ValueError("start must be non-negative.")

    def __call__(self, graph: AssetGraph):
        """Apply the wrapped policy when the current step matches the interval."""
        if self.step >= self.start and (self.step - self.start) % self.interval == 0:
            self.policy(graph)
        self.step += 1


def every(
    interval: int,
    policy: UpdatePolicy,
    *,
    start: int = 0,
) -> UpdatePolicy:
    """Run a policy every ``interval`` steps starting from ``start``.

    Args:
        interval (int): Number of steps between policy applications.
        policy (UpdatePolicy): The wrapped policy.
        start (int): First step at which the policy becomes eligible.

    Returns:
        UpdatePolicy: A scheduled wrapper around ``policy``.
    """
    return EveryPolicy(interval=interval, policy=policy, start=start)
