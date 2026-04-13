"""Run a policy only once."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from eclypse.utils.types import UpdatePolicy


@dataclass(slots=True)
class OnceAtPolicy:
    """Run a policy only once at the specified step."""

    step_at: int
    policy: UpdatePolicy
    step: int = 0

    def __post_init__(self):
        """Validate the schedule configuration."""
        if self.step_at < 0:
            raise ValueError("step_at must be non-negative.")

    def __call__(self, graph):
        """Apply the wrapped policy when the configured step is reached."""
        if self.step == self.step_at:
            self.policy(graph)
        self.step += 1


def once_at(
    step_at: int,
    policy: UpdatePolicy,
) -> UpdatePolicy:
    """Run a policy only once at the specified step.

    Args:
        step_at (int): Step at which the policy should run.
        policy (UpdatePolicy): The wrapped policy.

    Returns:
        UpdatePolicy: A scheduled wrapper around ``policy``.
    """
    return OnceAtPolicy(step_at=step_at, policy=policy)
