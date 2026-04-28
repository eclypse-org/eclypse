"""Run a policy according to a probability."""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from eclypse.policies._helpers import validate_probability

if TYPE_CHECKING:
    from eclypse.graph.asset_graph import AssetGraph
    from eclypse.utils.types import UpdatePolicy


@dataclass(slots=True)
class WithProbabilityPolicy:
    """Run a policy when a graph RNG draw is below ``probability``."""

    probability: float
    policy: UpdatePolicy

    def __post_init__(self):
        """Validate the schedule configuration."""
        validate_probability("probability", self.probability)

    def __call__(self, graph: AssetGraph):
        """Apply the wrapped policy after a successful random draw."""
        if graph.rnd.random() < self.probability:
            self.policy(graph)
            graph.logger.trace("Triggered with_probability policy.")


def with_probability(probability: float, policy: UpdatePolicy) -> UpdatePolicy:
    """Run a policy according to a probability.

    Args:
        probability (float): Per-call probability of triggering the policy.
        policy (UpdatePolicy): Wrapped policy to call.

    Returns:
        Policy that applies the wrapped policy after successful random draws.
    """
    return WithProbabilityPolicy(probability=probability, policy=policy)
