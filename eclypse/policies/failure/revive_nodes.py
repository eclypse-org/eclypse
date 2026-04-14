"""Random node revival policy."""

from __future__ import annotations

from typing import TYPE_CHECKING

from eclypse.policies._filters import (
    ensure_numeric_value,
    iter_selected_nodes,
)
from eclypse.policies.failure._helpers import validate_probability
from eclypse.utils.constants import MIN_AVAILABILITY

if TYPE_CHECKING:
    from eclypse.policies._filters import NodeFilter
    from eclypse.utils.types import UpdatePolicy


def revive_nodes(
    probability: float,
    *,
    availability: float = 0.99,
    availability_key: str = "availability",
    unavailable_at_or_below: float = MIN_AVAILABILITY,
    node_ids: list[str] | None = None,
    node_filter: NodeFilter | None = None,
) -> UpdatePolicy:
    """Randomly restore selected unavailable nodes.

    Args:
        probability (float): Probability of reviving each selected unavailable node.
        availability (float): Availability value assigned to revived nodes.
        availability_key (str): Node asset storing availability.
        unavailable_at_or_below (float): Threshold below which a node is considered
            unavailable.
        node_ids (list[str] | None): Optional explicit list of node ids to target.
        node_filter (NodeFilter | None): Optional predicate to filter target nodes.

    Returns:
        UpdatePolicy: A graph update policy implementing node revival.
    """
    validate_probability("probability", probability)

    def policy(graph):
        for _, data in iter_selected_nodes(
            graph,
            node_ids=node_ids,
            node_filter=node_filter,
        ):
            current = ensure_numeric_value(availability_key, data[availability_key])
            if current <= unavailable_at_or_below and graph.rnd.random() < probability:
                data[availability_key] = availability

    return policy
