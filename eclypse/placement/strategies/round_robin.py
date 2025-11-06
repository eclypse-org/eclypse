"""Module for the RoundRobin placement strategy.

A `PlacementStrategy` that attempts to distribute services across nodes,
in a round-robin fashion.
"""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Optional,
)

from .strategy import PlacementStrategy

if TYPE_CHECKING:
    from eclypse.graph import (
        Application,
        Infrastructure,
    )
    from eclypse.placement import (
        Placement,
        PlacementView,
    )


class RoundRobinStrategy(PlacementStrategy):
    """RoundRobin class.

    A `PlacementStrategy` that attempts to distribute services across nodes, in a
    round-robin fashion.
    """

    def __init__(self, sort_fn: Optional[Callable[[Any], Any]] = None):
        """Initializes the `RoundRobin` placement strategy.

        Args:
            sort_fn (Optional[Callable[[Any], Any]], optional): A function to sort the
            infrastructure nodes. Defaults to None.
        """
        self.sort_fn = sort_fn
        super().__init__()

    def place(
        self,
        _: Infrastructure,
        application: Application,
        __: Dict[str, Placement],
        placement_view: PlacementView,
    ) -> Dict[Any, Any]:
        """Performs the placement according to a round-robin logic.

        Places the services of an application on the infrastructure nodes, attempting
        to distribute them evenly.

        Args:
            _ (Infrastructure): The infrastructure to place the application on.
            application (Application): The application to place on the infrastructure.
            __ (Dict[str, Placement]): The placement of all the applications in the simulations.
            placement_view (PlacementView): The snapshot of the current state of the infrastructure.

        Returns:
            Dict[str, str]: A mapping of services to infrastructure nodes.
        """
        mapping = {}
        infrastructure_nodes = list(placement_view.residual.nodes(data=True))
        if self.sort_fn:
            infrastructure_nodes.sort(key=self.sort_fn)

        for service in application.nodes:
            selected_node, _ = infrastructure_nodes.pop(0)
            mapping[service] = selected_node

            infrastructure_nodes.append(selected_node)

        return mapping
