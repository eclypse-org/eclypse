"""Module for defining a placement strategy."""

from __future__ import annotations

from abc import abstractmethod
from typing import (
    TYPE_CHECKING,
    Dict,
)

from eclypse_core.placement import PlacementStrategy as _PlacementStrategy

if TYPE_CHECKING:
    from eclypse_core.placement import (
        Placement,
        PlacementView,
    )

    from eclypse.graph import (
        Application,
        Infrastructure,
    )


class PlacementStrategy(_PlacementStrategy):
    """A global placement strategy that places services of an application on
    infrastructure nodes."""

    @abstractmethod
    def place(
        self,
        infrastructure: Infrastructure,
        application: Application,
        placements: Dict[str, Placement],
        placement_view: PlacementView,
    ) -> Dict[str, str]:
        """Given an infrastructure, an application, a dictionary of placements, and a
        placement view, return a mapping of services IDs to node IDs, for the
        application.

        This method must be overridden by the user.

        Args:
            infrastructure (Infrastructure): The infrastructure to place the application onto.
            application (Application): The application to place onto the infrastructure.
            placements (Dict[str, Placement]): The placement of all the applications in the simulations.
            placement_view (PlacementView): The snapshot of the current state of the \
                infrastructure.

        Returns:
            Dict[str, str]: A dictionary mapping service IDs to node IDs, or None if the \
                application cannot be placed onto the infrastructure.
        """

    def is_feasible(self, infrastructure: Infrastructure, _: Application) -> bool:
        """Check if the application can be placed on the infrastructure.

        Default implementation checks if there are enough available nodes in the
        infrastructure.

        Args:
            infrastructure (Infrastructure): The infrastructure to place the application onto.
            application (Application): The application to place onto the infrastructure.

        Returns:
            bool: True if the application can be placed on the infrastructure, False \
                otherwise.
        """
        return len(list(infrastructure.available.nodes)) > 0
