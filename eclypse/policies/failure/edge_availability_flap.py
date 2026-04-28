"""Edge availability flapping policy."""

from __future__ import annotations

from typing import TYPE_CHECKING

from eclypse.policies._filters import (
    ensure_numeric_value,
    iter_selected_edges,
)
from eclypse.policies._helpers import validate_probability
from eclypse.utils.constants import (
    MAX_AVAILABILITY,
    MIN_AVAILABILITY,
)

if TYPE_CHECKING:
    from eclypse.graph.asset_graph import AssetGraph
    from eclypse.policies._filters import EdgeFilter
    from eclypse.utils.types import UpdatePolicy


def edge_availability_flap(
    down_probability: float,
    *,
    up_probability: float | None = None,
    down_availability: float = MIN_AVAILABILITY,
    up_availability: float = MAX_AVAILABILITY,
    availability_key: str = "availability",
    unavailable_at_or_below: float = MIN_AVAILABILITY,
    edge_ids: list[tuple[str, str]] | None = None,
    edge_filter: EdgeFilter | None = None,
) -> UpdatePolicy:
    """Toggle edge availability up and down according to probabilities.

    Args:
        down_probability (float): Probability of moving an available edge down.
        up_probability (float | None): Probability of moving an unavailable edge up. When
            omitted, ``down_probability`` is reused.
        down_availability (float): Availability value for unavailable edges.
        up_availability (float): Availability value for recovered edges.
        availability_key (str): Edge asset used to store availability.
        unavailable_at_or_below (float): Threshold for considering an edge unavailable.
        edge_ids (list[tuple[str, str]] | None): Optional explicit edge identifiers to mutate.
        edge_filter (EdgeFilter | None): Optional predicate receiving ``(source, target, data)``.

    Returns:
        Policy that flips selected edge availability.
    """
    validate_probability("down_probability", down_probability)
    validate_probability("up_probability", up_probability)
    effective_up_probability = (
        down_probability if up_probability is None else up_probability
    )

    def policy(graph: AssetGraph):
        for _, _, data in iter_selected_edges(
            graph,
            edge_ids=edge_ids,
            edge_filter=edge_filter,
        ):
            current = ensure_numeric_value(availability_key, data[availability_key])
            if current <= unavailable_at_or_below:
                if graph.rnd.random() < effective_up_probability:
                    data[availability_key] = up_availability
            elif graph.rnd.random() < down_probability:
                data[availability_key] = down_availability

        graph.logger.trace("Applied edge_availability_flap policy.")

    return policy
