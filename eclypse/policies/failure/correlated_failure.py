"""Correlated node failure policy."""

from __future__ import annotations

from collections import defaultdict
from typing import (
    TYPE_CHECKING,
    Any,
)

from eclypse.policies._filters import iter_selected_nodes
from eclypse.policies._helpers import validate_probability
from eclypse.utils.constants import MIN_AVAILABILITY

if TYPE_CHECKING:
    from eclypse.graph.asset_graph import AssetGraph
    from eclypse.policies._filters import NodeFilter
    from eclypse.utils.types import UpdatePolicy


def correlated_failure(
    probability: float,
    *,
    group_key: str,
    availability_key: str = "availability",
    failed_availability: float = MIN_AVAILABILITY,
    node_ids: list[str] | None = None,
    node_filter: NodeFilter | None = None,
) -> UpdatePolicy:
    """Fail all selected nodes sharing a group value together.

    Args:
        probability (float): Per-group probability of applying the failure.
        group_key (str): Node asset used to identify correlated groups.
        availability_key (str): Node asset used to store availability.
        failed_availability (float): Value written when a group fails.
        node_ids (list[str] | None): Optional explicit node identifiers to mutate.
        node_filter (NodeFilter | None): Optional predicate receiving ``(node_id, data)``.

    Returns:
        Policy that fails whole selected node groups.
    """
    validate_probability("probability", probability)

    def policy(graph: AssetGraph):
        groups: dict[Any, list[dict[str, Any]]] = defaultdict(list)
        for _, data in iter_selected_nodes(
            graph,
            node_ids=node_ids,
            node_filter=node_filter,
        ):
            if group_key in data:
                groups[data[group_key]].append(data)

        for nodes in groups.values():
            if graph.rnd.random() < probability:
                for data in nodes:
                    data[availability_key] = failed_availability

        graph.logger.trace("Applied correlated_failure policy.")

    return policy
