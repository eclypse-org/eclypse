"""Module for a First Fit placement strategy.

It overrides the `place` method of the
PlacementStrategy class to place services of an application on infrastructure nodes
based on the first node that satisfies the requirements of the service.
"""

from __future__ import annotations

import random as rnd
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


class FirstFitStrategy(PlacementStrategy):
    """A placement strategy that places services onto the first node that satisfies the
    requirements."""

    def __init__(self, sort_fn: Optional[Callable[[Any], Any]] = None):
        """Initializes the FirstFit placement strategy.

        Args:
            sort_fn (Optional[Callable[[Any], Any]], optional): A function to sort \
                the infrastructure nodes. Defaults to None.
        """
        self.sort_fn = sort_fn
        super().__init__()

    def place(
        self,
        infrastructure: Infrastructure,
        application: Application,
        _: Dict[str, Placement],
        placement_view: PlacementView,
    ) -> Dict[str, str]:
        """Places the services of an application on the infrastructure nodes based on
        the first node that satisfies the requirements of the service.

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
        else:
            rnd.shuffle(infrastructure_nodes)

        for service, sattr in application.nodes(data=True):
            for node, nattr in infrastructure_nodes:
                if infrastructure.node_assets.satisfies(nattr, sattr):
                    mapping[service] = node
                    new_res = infrastructure.node_assets.consume(nattr, sattr)
                    infrastructure_nodes.remove((node, nattr))
                    infrastructure_nodes.append((node, new_res))
                    break
        return mapping
