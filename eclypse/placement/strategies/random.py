"""Module for the Random placement strategy.

It overrides the `place` method of the
PlacementStrategy class to place services of an application on infrastructure nodes
randomly.
"""

from __future__ import annotations

import os
import random as rnd
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Optional,
)

from eclypse_core.utils.constants import RND_SEED

from eclypse.placement import PlacementView

from .strategy import PlacementStrategy

if TYPE_CHECKING:
    from eclypse_core.placement import Placement

    from eclypse.graph import (
        Application,
        Infrastructure,
    )


class RandomStrategy(PlacementStrategy):
    """A placement strategy that places services randomly onto nodes."""

    def __init__(self, spread: bool = False, seed: Optional[int] = None):
        """Initializes the Random placement strategy.

        Args:
            spread (bool, optional): Whether to spread the services across different nodes. \
                Defaults to False.
            seed (Optional[int], optional): The seed for the random number generator. \
                Defaults to None.
        """
        self._rnd = rnd.Random(seed if seed is not None else os.environ[RND_SEED])
        self.spread = spread
        super().__init__()

    def place(
        self,
        infrastructure: Infrastructure,
        application: Application,
        _: Dict[str, Placement],
        __: PlacementView,
    ) -> Dict[Any, Any]:
        """Places the services of an application on the infrastructure nodes, randomly.

        Args:
            infrastructure (Infrastructure): The infrastructure to place the application on.
            application (Application): The application to place on the infrastructure.
            _ (Dict[str, Placement]): The placement of all the applications in the simulations.
            __ (PlacementView): The snapshot of the current state of the \
                infrastructure.

        Returns:
            Dict[str, str]: A mapping of services to infrastructure nodes.
        """

        infrastructure_nodes = list(infrastructure.available.nodes())
        if not infrastructure_nodes:
            return {}

        self._rnd.shuffle(infrastructure_nodes)

        if self.spread:
            return {
                service: infrastructure_nodes[i % len(infrastructure_nodes)]
                for i, service in enumerate(application.nodes)
            }

        return {
            service: self._rnd.choice(infrastructure_nodes)
            for service in application.nodes
        }
