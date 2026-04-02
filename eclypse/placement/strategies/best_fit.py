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


class BestFitStrategy(PlacementStrategy):
    """BestFitStrategy class.

    A placement strategy that places services onto the node that best fits the
    requirements.
    """

    def place(
        self,
        infrastructure: Infrastructure,
        application: Application,
        _: dict[str, Placement],
        placement_view: PlacementView,
    ) -> dict[Any, Any]:
        """Performs the placement according to a best-fit logic.

        Places the services of an application on the infrastructure nodes based on
        the node that best fits the requirements of the service.

        Args:
            infrastructure (Infrastructure): The infrastructure to place the application on.
            application (Application): The application to place on the infrastructure.
            _ (dict[str, Placement]): The placement of all the applications in the simulations.
            placement_view (PlacementView): The snapshot of the current state of the \
                infrastructure.

        Returns:
            dict[str, str]: A mapping of services to infrastructure nodes.
        """
        if not self.is_feasible(infrastructure, application):
            return {}

        mapping = {}
        infrastructure_nodes = list(placement_view.residual.nodes(data=True))
        rnd.shuffle(infrastructure_nodes)

        for service, sattr in application.nodes(data=True):
            best_fit: str | None = None
            best_nattr: dict[str, Any] | None = None
            best_idx: int | None = None
            for idx, (node, nattr) in enumerate(infrastructure_nodes):
                if infrastructure.node_assets.satisfies(nattr, sattr) and (
                    best_fit is None
                    or infrastructure.node_assets.satisfies(
                        placement_view.residual.nodes[best_fit], nattr
                    )
                ):
                    best_fit = node
                    best_nattr = nattr
                    best_idx = idx
            mapping[service] = best_fit
            if best_fit is None or best_nattr is None or best_idx is None:
                continue

            infrastructure_nodes[best_idx] = (
                best_fit,
                infrastructure.node_assets.consume(best_nattr, sattr),
            )
        return mapping
