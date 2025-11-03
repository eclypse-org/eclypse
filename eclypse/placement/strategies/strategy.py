"""Module for defining a global placement strategy.

It provides an abstract class that must be implemented by the user to define a global
placement strategy for the entire infrastructure.
"""

from __future__ import annotations

from abc import (
    ABC,
    abstractmethod,
)
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
)

if TYPE_CHECKING:
    from eclypse.graph import (
        Application,
        Infrastructure,
    )
    from eclypse.placement import (
        Placement,
        PlacementView,
    )


class PlacementStrategy(ABC):
    """PlacementStrategy abstract class.

    A global placement strategy that places services of an application on infrastructure nodes.
    """

    @abstractmethod
    def place(
        self,
        infrastructure: Infrastructure,
        application: Application,
        placements: Dict[str, Placement],
        placement_view: PlacementView,
    ) -> Dict[Any, Any]:
        """Defines the placement logic.

        Given an infrastructure, an application, a dictionary of placements, and a
        placement view, return a mapping of services IDs to node IDs, for the
        application.

        This method must be overridden by the user.

        Args:
            infrastructure (Infrastructure): The infrastructure to place the application onto.
            application (Application): The application to place onto the infrastructure.
            placements (Dict[str, Placement]): A dictionary of placements.
            placement_view (PlacementView): The placement view to use for the placement.

        Returns:
            Dict[Any, Any]: A dictionary mapping service IDs to node IDs, or None if the \
                application cannot be placed onto the infrastructure.
        """

    def is_feasible(
        self,
        infrastructure: Infrastructure,
        _: Application,  # pylint: disable=unused-argument
    ) -> bool:
        """Check if the application can be placed on the infrastructure.

        Args:
            infrastructure (Infrastructure): The infrastructure to place the application onto.
            application (Application): The application to place onto the infrastructure.

        Returns:
            bool: True if the application can be placed on the infrastructure, False \
                otherwise.
        """
        return len(list(infrastructure.available.nodes)) > 0
