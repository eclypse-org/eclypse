"""Module that contains the `RoundRobin` class, a `PlacementStrategy` that attempts to
distribute services across nodes, in a round-robin fashion."""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Dict,
    Optional,
)

from eclypse_core.placement import PlacementView

from .strategy import PlacementStrategy

if TYPE_CHECKING:
    from eclypse_core.placement import Placement

    from eclypse.graph import (
        Application,
        Infrastructure,
    )


class RoundRobinStrategy(PlacementStrategy):
    """A `PlacementStrategy` that attempts to distribute services across nodes, in a
    round-robin fashion."""

    def __init__(self, sort_fn: Optional[Callable[[Any], Any]] = None):
        """Initializes the `RoundRobin` placement strategy.

        Args:
            sort_fn (Optional[Callable[[Any], Any]], optional): A function to sort the \
                infrastructure nodes. Defaults to None.
        """

        self.sort_fn = sort_fn
        super().__init__()

    def place(
        self,
        infrastructure: Infrastructure,
        application: Application,
        _: Dict[str, Placement],
        placement_view: PlacementView,
    ) -> Dict[Any, Any]:
        """Places the services of an application on the infrastructure nodes, attempting
        to distribute them evenly.

        Args:
            infrastructure (Infrastructure): The infrastructure to place the application on.
            application (Application): The application to place on the infrastructure.
            _ (Dict[str, Placement]): The placement of all the applications in the simulations.
            placement_view (PlacementView): The snapshot of the current state of the \
                infrastructure.

        Returns:
            Dict[str, str]: A mapping of services to infrastructure nodes.
        """
        if not self.is_feasible(infrastructure, application):
            return {}
        mapping = {}
        infrastructure_nodes = list(placement_view.residual.available.nodes(data=True))
        if self.sort_fn:
            infrastructure_nodes.sort(key=self.sort_fn)

        for service in application.nodes:
            selected_node, _ = infrastructure_nodes.pop(0)
            mapping[service] = selected_node

            infrastructure_nodes.append(selected_node)

        return mapping
