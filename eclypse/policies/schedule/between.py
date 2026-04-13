"""Run a policy between two step bounds."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from eclypse.utils.types import UpdatePolicy


@dataclass(slots=True)
class BetweenPolicy:
    """Run a policy between two inclusive step bounds."""

    start: int
    end: int
    policy: UpdatePolicy
    step: int = 0

    def __post_init__(self):
        """Validate the schedule configuration."""
        if self.start < 0:
            raise ValueError("start must be non-negative.")
        if self.end < self.start:
            raise ValueError("end must be greater than or equal to start.")

    def __call__(self, graph):
        """Apply the wrapped policy while the current step is within bounds."""
        if self.start <= self.step <= self.end:
            self.policy(graph)
        self.step += 1


def between(
    start: int,
    end: int,
    policy: UpdatePolicy,
) -> UpdatePolicy:
    """Run a policy between two inclusive step bounds.

    Args:
        start (int): First step at which the policy should run.
        end (int): Last step at which the policy should run.
        policy (UpdatePolicy): The wrapped policy.

    Returns:
        UpdatePolicy: A scheduled wrapper around ``policy``.
    """
    return BetweenPolicy(start=start, end=end, policy=policy)
