"""Edge recovery policy."""

from __future__ import annotations

from typing import TYPE_CHECKING

from eclypse.policies._filters import iter_selected_edges
from eclypse.policies._helpers import validate_probability
from eclypse.policies.failure._helpers import set_availability_with_probability
from eclypse.utils.constants import MAX_AVAILABILITY

if TYPE_CHECKING:
    from eclypse.graph.asset_graph import AssetGraph
    from eclypse.policies._filters import EdgeFilter
    from eclypse.utils.types import UpdatePolicy


def revive_edges(
    probability: float,
    *,
    availability_key: str = "availability",
    revived_availability: float = MAX_AVAILABILITY,
    edge_ids: list[tuple[str, str]] | None = None,
    edge_filter: EdgeFilter | None = None,
) -> UpdatePolicy:
    """Mark selected edges as available according to ``probability``.

    Args:
        probability (float): Per-edge probability of applying the recovery.
        availability_key (str): Edge asset used to store availability.
        revived_availability (float): Value written when an edge recovers.
        edge_ids (list[tuple[str, str]] | None): Optional explicit edge identifiers to mutate.
        edge_filter (EdgeFilter | None): Optional predicate receiving ``(source, target, data)``.

    Returns:
        Policy that marks selected edges as recovered.
    """
    validate_probability("probability", probability)

    def policy(graph: AssetGraph):
        for _, _, data in iter_selected_edges(
            graph,
            edge_ids=edge_ids,
            edge_filter=edge_filter,
        ):
            set_availability_with_probability(
                data,
                probability=probability,
                availability_key=availability_key,
                target_availability=revived_availability,
                random=graph.rnd,
            )

        graph.logger.trace("Applied revive_edges policy.")

    return policy
