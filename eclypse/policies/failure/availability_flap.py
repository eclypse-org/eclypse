"""Availability flapping policy."""

from __future__ import annotations

from typing import TYPE_CHECKING

from eclypse.policies._filters import (
    ensure_numeric_value,
    iter_selected_nodes,
)
from eclypse.policies.failure._helpers import validate_probability
from eclypse.utils.constants import (
    MAX_AVAILABILITY,
    MIN_AVAILABILITY,
)

if TYPE_CHECKING:
    from eclypse.policies._filters import NodeFilter
    from eclypse.utils.types import UpdatePolicy


def availability_flap(
    down_probability: float,
    *,
    up_probability: float | None = None,
    down_availability: float = MIN_AVAILABILITY,
    up_availability: float = MAX_AVAILABILITY,
    availability_key: str = "availability",
    unavailable_at_or_below: float = MIN_AVAILABILITY,
    node_ids: list[str] | None = None,
    node_filter: NodeFilter | None = None,
) -> UpdatePolicy:
    """Toggle node availability up and down according to separate probabilities.

    Args:
        down_probability (float): Probability of taking an available node down.
        up_probability (float | None): Probability of restoring an unavailable node.
            Defaults to ``down_probability`` when omitted.
        down_availability (float): Availability value assigned to failed nodes.
        up_availability (float): Availability value assigned to restored nodes.
        availability_key (str): Node asset storing availability.
        unavailable_at_or_below (float): Threshold below which a node is considered
            unavailable.
        node_ids (list[str] | None): Optional explicit list of node ids to target.
        node_filter (NodeFilter | None): Optional predicate to filter target nodes.

    Returns:
        UpdatePolicy: A graph update policy implementing flapping behaviour.
    """
    validate_probability("down_probability", down_probability)
    validate_probability("up_probability", up_probability)
    effective_up_probability = (
        down_probability if up_probability is None else up_probability
    )

    def policy(graph):
        for _, data in iter_selected_nodes(
            graph,
            node_ids=node_ids,
            node_filter=node_filter,
        ):
            current = ensure_numeric_value(availability_key, data[availability_key])
            if current <= unavailable_at_or_below:
                if graph.rnd.random() < effective_up_probability:
                    data[availability_key] = up_availability
            elif graph.rnd.random() < down_probability:
                data[availability_key] = down_availability

    return policy
