"""Run a policy with a minimum gap between applications."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from eclypse.graph.asset_graph import AssetGraph
    from eclypse.utils.types import UpdatePolicy


@dataclass(slots=True)
class CooldownPolicy:
    """Run a policy at most once every ``steps`` calls."""

    steps: int
    policy: UpdatePolicy
    step: int = 0
    next_allowed_step: int = 0

    def __post_init__(self):
        """Validate the schedule configuration."""
        if self.steps < 0:
            raise ValueError("steps must be non-negative.")

    def __call__(self, graph: AssetGraph):
        """Apply the wrapped policy when the cooldown has elapsed."""
        if self.step >= self.next_allowed_step:
            self.policy(graph)
            self.next_allowed_step = self.step + self.steps + 1
            graph.logger.trace(f"Triggered cooldown policy at step {self.step}.")
        self.step += 1


def cooldown(steps: int, policy: UpdatePolicy) -> UpdatePolicy:
    """Run a policy at most once every ``steps`` calls.

    Args:
        steps (int): Minimum number of skipped calls after each application.
        policy (UpdatePolicy): Wrapped policy to throttle.

    Returns:
        Stateful schedule policy.
    """
    return CooldownPolicy(steps=steps, policy=policy)
