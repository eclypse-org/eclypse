"""Module for a Best Fit placement strategy.

It overrides the `place` method of the
PlacementStrategy class to place services of an application on infrastructure nodes
based on the node that best fits the requirements of the service (i.e., the node that
satisfies the requirements and has the least amount of resources left after the placement).
"""

from __future__ import annotations

import random as rnd
from typing import (
    TYPE_CHECKING,
    Any,
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


class BestFitStrategy(PlacementStrategy):
    """A placement strategy that places services onto the node that best fits the
    requirements."""

    def place(
        self,
        infrastructure: Infrastructure,
        application: Application,
        _: Dict[str, Placement],
        placement_view: PlacementView,
    ) -> Dict[Any, Any]:
        """Places the services of an application on the infrastructure nodes based on
        the node that best fits the requirements of the service.

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
        rnd.shuffle(infrastructure_nodes)

        for service, sattr in application.nodes(data=True):
            best_fit: Optional[str] = None
            best_nattr: Optional[Dict[str, Any]] = None
            for node, nattr in infrastructure_nodes:
                if infrastructure.node_assets.satisfies(nattr, sattr):
                    if best_fit is None or infrastructure.node_assets.satisfies(
                        placement_view.residual.nodes[best_fit], nattr
                    ):
                        best_fit = node
                        best_nattr = nattr
            mapping[service] = best_fit
            if best_fit is None or best_nattr is None:
                continue

            new_res = infrastructure.node_assets.consume(best_nattr, sattr)
            infrastructure_nodes.remove((best_fit, best_nattr))
            infrastructure_nodes.append((best_fit, new_res))
        return mapping
