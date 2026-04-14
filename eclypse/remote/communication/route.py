"""Module for the Route class.

A route connects two neighbor services in an application through several infrastructure
nodes, and is modelled as a list of hops (node IDs).
"""

from __future__ import annotations

from dataclasses import (
    dataclass,
    field,
)
from sys import getsizeof
from typing import (
    Any,
)

from eclypse.utils.constants import MIN_LATENCY

MILLISECONDS_PER_SECOND = 1000
"""Number of milliseconds in one second."""

BYTES_TO_MEGABITS = 8e-6
"""Conversion factor from bytes to megabits."""


@dataclass(slots=True)
class Route:
    """A route which connects two neighbor services in an application.

    It contains the sender and recipient IDs, the sender and recipient node IDs, the
    list of hops (i.e., triplets denoting source node of the hop, target node of the
    hop, and cost of the link).
    """

    sender_id: str
    """The ID of the sender service."""

    sender_node_id: str
    """The ID of the infrastructure node hosting the sender service."""

    recipient_id: str
    """The ID of the recipient service."""

    recipient_node_id: str
    """The ID of the infrastructure node hosting the recipient service."""

    processing_time: float
    """The processing time contributed by the nodes traversed by the route."""

    hops: list[tuple[str, str, dict[str, Any]]] = field(default_factory=list)
    """The ordered infrastructure hops of the route."""

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
        msg_size = _get_bytes_size(msg)
        return self.processing_time / MILLISECONDS_PER_SECOND + sum(
            (msg_size * BYTES_TO_MEGABITS / link.get("bandwidth", float("inf")))
            + (link.get("latency", MIN_LATENCY) / MILLISECONDS_PER_SECOND)
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


def _get_bytes_size(data: Any) -> int:
    """Return the size of an object in bytes.

    The size is computed according to the following rules:

    - int, float, str, bool: the size is the size of the object itself.
    - list, tuple, set: the size is the sum of the sizes of the
      elements in the collection.
    - dict: the size is the sum of the sizes of the keys and values in the dictionary.
    - objects with a ``__dict__`` attribute: the size is the size of the
      ``__dict__`` attribute.
    - other objects: the size is the size of the object itself, computed using
      ``sys.getsizeof``.

    Args:
        data (Any): The object to be measured.

    Returns:
        int: The size of the object in bytes.
    """
    if isinstance(data, (int, float, str, bool)):
        return getsizeof(data)
    if isinstance(data, (list, tuple, set)):
        return sum(_get_bytes_size(element) for element in data)
    if isinstance(data, dict):
        return sum(
            _get_bytes_size(key) + _get_bytes_size(value) for key, value in data.items()
        )
    if hasattr(data, "__dict__"):
        return _get_bytes_size(data.__dict__)
    return getsizeof(data)
