from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Dict,
    List,
    Optional,
)

from eclypse_core.simulation.simulator.remote import RemoteSimulator

if TYPE_CHECKING:
    from eclypse_core.placement import Placement
    from eclypse_core.placement.strategy import PlacementStrategy
    from eclypse_core.placement.view import PlacementView
    from eclypse_core.simulation.simulator.local import SimulationState
    from eclypse_core.utils.logging import Logger
    from eclypse.graph.application import Application


class RemoteSimulator:

    def __init__(self, *args, **kwargs):
        self._engine = RemoteSimulator(*args, **kwargs)

    def start(self):
        """Starts the simulation."""
        self._engine.start()

    def enact(self):
        """Enacts the placements within the remote infrastructure."""
        self._engine.enact()

    async def run(self):
        """Run the simulation."""
        return await self._engine.run()

    async def fire(self):
        return await self._engine.fire()

    async def stop(self):
        """Stops the simulation."""
        return await self._engine.stop()

    async def trigger(self, event_name: str, **kwargs):
        """Triggers an event in the simulation."""
        return await self._engine.trigger(event_name, **kwargs)

    async def get_feed(self, event_name: str):
        return await self._engine.get_feed(event_name)

    async def wait(self, timeout: Optional[float] = None):
        """Wait for the simulation to finish."""
        return await self._engine.wait(timeout)

    def register(
        self,
        application: Application,
        placement_strategy: Optional[PlacementStrategy] = None,
    ):
        """Include an application in the simulation. A placement strategy must be
        provided.

        Args:
            application (Application): The application to include.
            placement_strategy (PlacementStrategy): The placement strategy to use.
        """
        self._engine.register(application, placement_strategy)

    def cleanup(self):
        self._engine.cleanup()

    async def route(self, application_id: str, source_id: str, dest_id: str, **kwargs):
        """Computes the route between two logically neighbor services. If the services
        are not logically neighbors, it returns None.

        Args:
            source_id (str): The ID of the source service.
            dest_id (str): The ID of the destination service.

        Returns:
            Route: The route between the two services.
        """
        return await self._engine.route(application_id, source_id, dest_id, **kwargs)

    async def get_neighbors(self, application_id: str, service_id: str) -> List[str]:
        """Returns the logical neighbors of a service in an application.

        Args:
            service_id (str): The ID of the service for which to retrieve the neighbors.

        Returns:
            List[str]: A list of service IDs.
        """
        return await self._engine.get_neighbors(application_id, service_id)

    def get_status(self):
        """Returns the status of the simulation."""
        return self._engine.get_status()

    def get_report(self):
        """Returns the report of the simulation."""
        return self._engine.get_report()

    @property
    def id(self) -> str:
        """Returns the ID of the infrastructure manager."""
        return self._engine.id

    @property
    def remote(self) -> bool:
        """Returns True if the simulation is remote, False otherwise."""
        return self._engine.remote

    @property
    def placements(self) -> Dict[str, Placement]:
        """Get the placements of the applications in the simulation.

        Returns:
            Dict[str, Placement]: The placements of the applications.
        """
        return self._engine.placements

    @property
    def placement_view(self) -> PlacementView:
        """Get the placement view of the simulation.

        Returns:
            PlacementView: The placement view of the simulation.
        """
        return self._engine.placement_view

    @property
    def applications(self) -> List[Application]:
        """Get the applications included in the simulation.

        Returns:
            List[Application]: The list of Applications.
        """
        return [p.application for p in self.placements.values()]

    @property
    def logger(self) -> Logger:
        """Get the logger of the simulation.

        Returns:
            EclypseLogger: The logger of the simulation.
        """
        return self._engine.logger.bind(id="Simulation")

    @property
    def status(self) -> SimulationState:
        """Get the state of the simulation.

        Returns:
            SimulationState: The state of the simulation.
        """
        return self._engine.status
