"""Module for the Route class.

A route connects two neighbor services in an application through several infrastructure
nodes, and is modelled as a list of hops (node IDs).
"""

from __future__ import annotations

from typing import (
    Any,
    Dict,
    List,
    Optional,
    Tuple,
)

from eclypse.utils.constants import MIN_LATENCY
from eclypse.utils.tools import get_bytes_size


class Route:
    """A route which connects two neighbor services in an application.

    It contains the sender and recipient IDs, the sender and recipient node IDs, the
    list of hops (i.e., triplets denoting source node of the hop, target node of the
    hop, and cost of the link).
    """

    def __init__(
        self,
        sender_id: str,
        sender_node_id: str,
        recipient_id: str,
        recipient_node_id: str,
        processing_time: float,
        hops: Optional[List[Tuple[str, str, Dict[str, Any]]]] = None,
    ):
        """Initializes a Route object.

        Args:
            sender_id (str): The ID of the sender service.
            sender_node_id (str): The ID of the node where the sender service is deployed.
            recipient_id (str): The ID of the recipient service.
            recipient_node_id (str): The ID of the node where the recipient service is \
                deployed.
            processing_time (float): The processing time of the nodes traversed by the \
                route.
            hops (Optional[List[Tuple[str, str, Dict[str, Any]]]]): The list \
                of hops in the route. Each hop is a triplet containing the source node \
                ID, the target node ID, and the cost of the link. Defaults to None.
        """
        self.sender_id = sender_id
        self.sender_node_id = sender_node_id
        self.recipient_id = recipient_id
        self.recipient_node_id = recipient_node_id
        self.processing_time = processing_time
        self.hops = hops if hops is not None else []

    def __len__(self) -> int:
        """Returns the number of hops in the route.

        Returns:
            int: The number of hops.
        """
        return len(self.hops)

    def cost(self, msg: Any) -> float:
        """Returns a function that computes the cost of the route for a given object.

        The object must be dict-like (i.e., it must have a __dict__ method).

        Args:
            msg (Any): The object for which to compute the cost (e.g., a message).

        Returns:
            float: The function that computes the cost of the route.
        """
        return self.processing_time / 1000 + sum(
            (get_bytes_size(msg) * 8 * 1e-6 / link.get("bandwidth", float("inf")))
            + (link.get("latency", MIN_LATENCY) / 1000)
            for _, _, link in self.hops
        )

    @property
    def network_cost(self):
        """Returns the network cost of the route.

        The network cost is computed as the sum of the costs of the links in the route.

        Returns:
            float: The network cost.
        """
        return self.cost([])

    @property
    def no_hop(self) -> bool:
        """Returns True if the sender and recipient are deployed on the same node.

        Returns:
            bool: True if the sender and recipient are deployed on the same node, \
                False otherwise.
        """
        return self.sender_node_id == self.recipient_node_id

    def __str__(self) -> str:
        """Returns a string representation of the route.

        Returns:
            str: The string representation of the route.
        """
        result = f"Path from {self.sender_id} ({self.sender_node_id}) "
        result += f"to {self.recipient_id} ({self.recipient_node_id}):\n"
        result += " -> ".join(f"{s} -- {t} ({link})" for s, t, link in self.hops)
        return result
