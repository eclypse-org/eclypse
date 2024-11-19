"""Module for the Static placement strategy.

It overrides the `place` method of the
PlacementStrategy class to place services of an application on infrastructure nodes
based on a predefined mapping of services to nodes in the form of a dictionary.
"""

from typing import (
    Any,
    Dict,
)

from .strategy import PlacementStrategy


class StaticStrategy(PlacementStrategy):
    """Static placement strategy based on a predefined mapping of services to nodes in
    the form of a dictionary."""

    def __init__(self, mapping: Dict[str, str]):
        """Initializes the StaticPlacementStrategy object.

        Args:
            mapping (Optional[Dict[str, str]]): A dictionary mapping service IDs to node IDs.
        """
        if not mapping:
            raise ValueError("Please provide a valid mapping of services to nodes.")

        self.mapping = mapping
        super().__init__()

    def place(self, *_) -> Dict[Any, Any]:
        """Returns the static mapping of services to nodes, given at initialization.

        Returns:
            Dict[str, str]: the static mapping.
        """
        return self.mapping
