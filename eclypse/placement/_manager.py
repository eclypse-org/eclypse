# pylint: disable=protected-access
"""Module for the PlacementManager class.

It manages the placement of applications in the infrastructure and is responsible for
the mapping phase, where the application services are mapped to the infrastructure nodes.
"""

from __future__ import annotations

from random import shuffle
from typing import (
    TYPE_CHECKING,
    Dict,
    Generator,
    List,
    Optional,
    Tuple,
)

from eclypse.placement import Placement
from eclypse.utils._logging import logger

from .view import PlacementView

if TYPE_CHECKING:
    from eclypse.graph import (
        Application,
        Infrastructure,
    )
    from eclypse.placement import PlacementStrategy
    from eclypse.utils._logging import Logger


class PlacementManager:
    """PlacementManager manages the placement of applications in the infrastructure."""

    def __init__(self, infrastructure: Infrastructure):
        """Initializes the PlacementManager.

        Args:
            infrastructure (Infrastructure): The infrastructure to place the applications onto.
        """
        self.infrastructure = infrastructure
        self.placements: Dict[str, Placement] = {}
        self.placement_view: PlacementView = PlacementView(self.infrastructure)

    def audit(self):
        """Check application placements and reset those violating infrastructure constraints.

        Iterates over the placements of all the involved applications, checking if
        the placement constraints are respected by the infrastructure capabilities.

        If not, it resets the placement of the applications whose requirements
        are not respected.
        """
        for _, not_respected in self.mapping_phase():
            if not_respected:
                for n, apps in self.placement_view.nodes_used_by.items():
                    if n in not_respected:
                        for app in apps:
                            p = self.get(app)
                            p._to_reset = True

    def enact(self):
        """Manage and apply (or reset) the placement of applications on the infrastructure."""
        for p in self.placements.values():
            if p._to_reset:
                self.logger.warning(f"Resetting placement of {p.application.id}")
                self.logger.trace(p)
                p._reset_mapping()

            if p.mapping:
                self.logger.log(
                    "ECLYPSE",
                    f"Placement of {p.application.id} on {self.infrastructure.id}",
                )
                self.logger.log("ECLYPSE", p)

    def generate_mapping(self, placement: Placement):
        """Create application-to-infrastructure mapping based on available placement strategy.

        Generate the mapping of the applications onto the infrastructure, using the
        placement strategy if available. If no placement strategy is available, the
        global one is used.

        Args:
            placement (Placement): The placement to generate the mapping for.
        """
        if placement.strategy is None:
            self.logger.trace(
                f"Using {self.infrastructure.strategy.__class__.__name__} "
                f" strategy for {placement.application.id}",
            )
            if self.infrastructure.has_strategy:
                placement.mapping = self.infrastructure.strategy.place(  # type: ignore[union-attr]
                    self.infrastructure,
                    placement.application,
                    self.placements,
                    self.placement_view,
                )
            else:
                raise ValueError(
                    f"No placement strategy provided for {placement.application.id}"
                )
        else:
            self.logger.trace(
                f"Using {placement.strategy.__class__.__name__} "
                f"strategy for {placement.application.id}"
            )
            placement._generate_mapping(self.placements, self.placement_view)

        if not placement.mapping or all(v is None for v in placement.mapping.values()):
            self.logger.log(
                "ECLYPSE", f"No placement found for {placement.application.id}"
            )
            placement._reset_mapping()
        elif not_placed_services := placement.is_partial:
            self.logger.warning(f"Partial placement for {placement.application.id}")
            self.logger.warning(f"Not placed services: {not_placed_services}")
            placement._reset_mapping()

    def mapping_phase(
        self,
    ) -> Generator[Tuple[Placement, List[str]], None, None]:
        """Executes the mapping phase of the placement.

        If the placement is incremental, it will return a generator of tuples containing
        the placement and the nodes that are not respected by the placement. If the
        placement is not incremental, it will return a list of such tuples.

        Returns:
            Generator[Tuple[Placement, List[str]], None, None]:
                A list of tuples containing the placement and the nodes that are not \
                respected by the placement, or a generator of such tuples.
        """
        self.placement_view._reset()
        placements = list(self.placements.values())

        shuffle(placements)
        for p in placements:
            if not p.mapping:
                self.generate_mapping(p)

            self.placement_view._update_view(p)

            not_respected = self.infrastructure.contains(self.placement_view)
            if not_respected:
                p._to_reset = True
            yield (p, not_respected)

    def register(
        self,
        application: Application,
        placement_strategy: Optional[PlacementStrategy] = None,
    ):
        """Include an application in the simulation.

        A placement strategy must be provided.

        Args:
            application (Application): The application to include.
            placement_strategy (PlacementStrategy): The placement strategy to use.
        """
        application.set_flows()
        self.placements[application.id] = Placement(
            infrastructure=self.infrastructure,
            application=application,
            strategy=placement_strategy,
        )

    def get(self, application_id: str) -> Placement:
        """Get the placement of an application.

        Args:
            application_id (str): The ID of the application.

        Returns:
            Placement: The placement of the application,

        Raises:
            KeyError: If the application is not found.
        """
        if application_id not in self.placements:
            raise KeyError(f"Application {application_id} not found.")

        return self.placements[application_id]

    @property
    def logger(self) -> Logger:
        """Get a logger for the PlacementManager.

        Returns:
            Logger: The logger for the PlacementManager.
        """
        return logger.bind(id="PlacementManager")
