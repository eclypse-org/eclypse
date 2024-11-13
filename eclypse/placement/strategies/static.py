"""Module for the Static placement strategy.

It overrides the `place` method of the
PlacementStrategy class to place services of an application on infrastructure nodes
based on a predefined mapping of services to nodes in the form of a dictionary.
"""

from typing import (
    Any,
    Dict,
    Optional,
)

from .strategy import PlacementStrategy


class StaticStrategy(PlacementStrategy):
    """Static placement strategy based on a predefined mapping of services to nodes in
    the form of a dictionary."""

    def __init__(self, mapping: Optional[Dict[str, str]] = None):
        """Initializes the StaticPlacementStrategy object.

        Args:
            mapping (Optional[Dict[str, str]]): A dictionary mapping service IDs to node IDs.
        """
        self.mapping = mapping if mapping is not None else {}

    def place(self, *_) -> Dict[Any, Any]:
        """Returns the static mapping of services to nodes.

        Returns:
            Dict[str, str]: the static mapping.
        """
        return self.mapping
