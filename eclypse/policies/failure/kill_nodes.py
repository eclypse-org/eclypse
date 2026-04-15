"""Random node failure policy."""

from __future__ import annotations

from typing import TYPE_CHECKING

from eclypse.policies._filters import (
    ensure_numeric_value,
    iter_selected_nodes,
)
from eclypse.policies.failure._helpers import validate_probability
from eclypse.utils.constants import MIN_AVAILABILITY

if TYPE_CHECKING:
    from eclypse.graph.asset_graph import AssetGraph
    from eclypse.policies._filters import NodeFilter
    from eclypse.utils.types import UpdatePolicy


def kill_nodes(
    probability: float,
    *,
    revive_probability: float | None = None,
    down_availability: float = MIN_AVAILABILITY,
    revived_availability: float = 0.99,
    availability_key: str = "availability",
    node_ids: list[str] | None = None,
    node_filter: NodeFilter | None = None,
) -> UpdatePolicy:
    """Randomly mark selected nodes as unavailable, with optional revival.

    Args:
        probability (float): Probability of marking a selected node as unavailable.
        revive_probability (float | None): Optional probability of reviving an
            unavailable selected node.
        down_availability (float): Availability value assigned to failed nodes.
        revived_availability (float): Availability value assigned to revived nodes.
        availability_key (str): Node asset storing availability.
        node_ids (list[str] | None): Optional explicit list of node ids to target.
        node_filter (NodeFilter | None): Optional predicate to filter target nodes.

    Returns:
        UpdatePolicy: A graph update policy implementing node failures.
    """
    validate_probability("probability", probability)
    validate_probability("revive_probability", revive_probability)

    def policy(graph: AssetGraph):
        for _, data in iter_selected_nodes(
            graph,
            node_ids=node_ids,
            node_filter=node_filter,
        ):
            availability = ensure_numeric_value(
                availability_key,
                data[availability_key],
            )
            if graph.rnd.random() < probability:
                data[availability_key] = down_availability
            elif (
                revive_probability is not None
                and availability <= down_availability
                and graph.rnd.random() < revive_probability
            ):
                data[availability_key] = revived_availability

        graph.logger.trace("Applied kill_nodes policy.")

    return policy
