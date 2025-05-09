"""Module for the Static placement strategy.

It overrides the `place` method of the
PlacementStrategy class to place services of an application on infrastructure nodes
based on a predefined mapping of services to nodes in the form of a dictionary.
"""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
)

from .strategy import PlacementStrategy

if TYPE_CHECKING:
    from eclypse_core.placement import (
        Placement,
        PlacementView,
    )

    from eclypse.graph import (
        Application,
        Infrastructure,
    )


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

    def place(
        self,
        infrastructure: Infrastructure,
        application: Application,
        _: Dict[str, Placement],
        __: PlacementView,
    ) -> Dict[Any, Any]:
        """Returns the static mapping of services to nodes, given at initialization.

        Returns:
            Dict[str, str]: the static mapping.
        """
        if not self.is_feasible(infrastructure, application):
            return {}
        return self.mapping

    def is_feasible(self, infrastructure: Infrastructure, _: Application) -> bool:
        """Check if the application can be placed on the infrastructure.

        It checks if all the nodes in the mapping are available in the infrastructure.
        """
        for node in self.mapping.values():
            if node not in infrastructure.nodes:
                infrastructure.logger.error(
                    f"Node {node} not found or not available in the infrastructure."
                )
                return False
        return True
