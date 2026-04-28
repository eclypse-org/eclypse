"""Run a policy at explicit steps."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from eclypse.graph.asset_graph import AssetGraph
    from eclypse.utils.types import UpdatePolicy


@dataclass(slots=True)
class AtPolicy:
    """Run a policy at selected steps."""

    steps: set[int]
    policy: UpdatePolicy
    step: int = 0

    def __post_init__(self):
        """Validate the schedule configuration."""
        if not self.steps:
            raise ValueError("steps must not be empty.")
        if any(step < 0 for step in self.steps):
            raise ValueError("steps must be non-negative.")

    def __call__(self, graph: AssetGraph):
        """Apply the wrapped policy when the current step is selected."""
        if self.step in self.steps:
            self.policy(graph)
            graph.logger.trace(f"Triggered at policy at step {self.step}.")
        self.step += 1


def at(steps: int | list[int] | tuple[int, ...], policy: UpdatePolicy) -> UpdatePolicy:
    """Run a policy at one or more explicit steps.

    Args:
        steps (int | list[int] | tuple[int, ...]):
            Step number or step numbers that trigger the policy.
        policy (UpdatePolicy): Wrapped policy to call when the step matches.

    Returns:
        Stateful schedule policy.
    """
    selected_steps = {steps} if isinstance(steps, int) else set(steps)
    return AtPolicy(steps=selected_steps, policy=policy)
