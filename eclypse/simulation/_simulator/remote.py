# mypy: disable-error-code="override"
# pylint: disable=protected-access
"""Module for the RemoteSimulator class.

It operates like the local simulator, but performs the simulation using ray actors.
It also performs operations on the Services placed on the infrastructure,
such as deploying, starting, stopping and undeploying them.

The RemoteSimulator is also the entry point for the communication between services, as
it ask to the infrastructure the computation of the routes between them, retrieving the
costs of such interactions.
"""

from __future__ import annotations

import asyncio
from datetime import timedelta
from typing import (
    List,
    Optional,
)

from eclypse.remote.communication.route import Route
from eclypse.utils._logging import config_logger
from eclypse.workflow.trigger.trigger import ScheduledTrigger

from .local import (
    SimulationState,
    Simulator,
)
from .ops_handler import RemoteSimOpsHandler


class RemoteSimulator(Simulator):
    """RemoteSimulator class.

    When a service needs to interact with another service, it communicates with the
    RemoteSimulator to define the current costs for such interaction.
    """

    def __init__(self, *args, **kwargs):
        config_logger()  # re-do for RemoteSimulator node
        self._engines = kwargs.pop("remotes")
        super().__init__(*args, **kwargs)

    def enact(self):
        """Enacts the placements within the remote infrastructure."""
        for p in self._manager.placements.values():
            if p._to_reset and p._deployed:
                RemoteSimOpsHandler.stop(p)
                RemoteSimOpsHandler.undeploy(p)
            elif not p._to_reset and p.mapping and not p._deployed:
                RemoteSimOpsHandler.deploy(p)
                RemoteSimOpsHandler.start(p)

        super().enact()

    async def wait(self, timeout: Optional[float] = None):
        # pylint: disable=invalid-overridden-method
        """Wait for the simulation to finish.

        Args:
            timeout (Optional[float]): The maximum time to wait for the simulation to
                finish. If None, it waits indefinitely. Defaults to None.
        """
        if timeout:
            stop_event = self._events["stop"]
            trigger = ScheduledTrigger(timedelta(seconds=timeout))
            trigger.init()
            stop_event.triggers.append(trigger)

        t0 = self._event_loop.time()
        while self._status != SimulationState.IDLE and (
            timeout is None or self._event_loop.time() - t0 < timeout
        ):
            await asyncio.sleep(0.5)

    def cleanup(self):
        """Cleans up the emulation status by stopping and undeploying all placements."""
        for p in self.placements.values():
            if p._deployed:
                RemoteSimOpsHandler.stop(p)
                RemoteSimOpsHandler.undeploy(p)

    async def route(
        self,
        application_id: str,
        source_id: str,
        dest_id: str,
    ) -> Optional[Route]:
        """Computes the route between two logically neighbor services.

        If the services are not logically neighbors, it returns None.

        Args:
            application_id (str): The ID of the application.
            source_id (str): The ID of the source service.
            dest_id (str): The ID of the destination service.

        Returns:
            Route: The route between the two services.
        """
        n = await self.get_neighbors(application_id, source_id)
        if dest_id not in n:
            return None

        placement = self._manager.get(application_id)
        try:
            source_node = placement.service_placement(source_id)
            dest_node = placement.service_placement(dest_id)
        except KeyError:
            return None

        path = (
            self.infrastructure.path(source_node, dest_node)
            if source_node != dest_node
            else ([], 0)
        )

        return (
            None
            if path is None
            else Route(
                sender_id=source_id,
                sender_node_id=source_node,
                recipient_id=dest_id,
                recipient_node_id=dest_node,
                processing_time=path[1],
                hops=path[0],
            )
        )

    async def get_neighbors(self, application_id: str, service_id: str) -> List[str]:
        """Returns the logical neighbors of a service in an application.

        Args:
            application_id (str): The ID of the application.
            service_id (str): The ID of the service for which to retrieve the neighbors.

        Returns:
            List[str]: A list of service IDs.
        """
        application = self._manager.get(application_id).application
        neighbors = list(application.neighbors(service_id))
        return neighbors

    def get_status(self):
        """Returns the status of the simulation."""
        return self._status

    @property
    def id(self) -> str:
        """Returns the ID of the infrastructure manager."""
        return f"{self.infrastructure.id}/manager"

    @property
    def remote(self) -> bool:
        """Returns True if the simulation is remote, False otherwise."""
        return True
