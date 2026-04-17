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

from eclypse.remote.communication.route import Route
from eclypse.utils._logging import config_logger

from .local import (
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
            if p.reset_requested and p.deployed:
                RemoteSimOpsHandler.stop(p)
                RemoteSimOpsHandler.undeploy(p)
            elif not p.reset_requested and p.mapping and not p.deployed:
                RemoteSimOpsHandler.deploy(p)
                RemoteSimOpsHandler.start(p)

        super().enact()

    async def wait(self, timeout: float | None = None):
        # pylint: disable=invalid-overridden-method
        """Wait for the simulation to finish.

        Args:
            timeout (float | None): The maximum time to wait for the simulation to
                finish. If None, it waits indefinitely. Defaults to None.
        """
        await asyncio.to_thread(super().wait, timeout)

    def cleanup(self):
        """Cleans up the emulation status by stopping and undeploying all placements."""
        for p in self.placements.values():
            if p.deployed:
                RemoteSimOpsHandler.stop(p)
                RemoteSimOpsHandler.undeploy(p)

    async def _finalize_shutdown(self):
        """Stop remote services before flushing local simulator resources."""
        try:
            self.cleanup()
        finally:
            await super()._finalize_shutdown()

    async def route(
        self,
        application_id: str,
        source_id: str,
        dest_id: str,
    ) -> Route | None:
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
            else []
        )

        if path is None:
            return None

        return Route(
            sender_id=source_id,
            sender_node_id=source_node,
            recipient_id=dest_id,
            recipient_node_id=dest_node,
            processing_time=self.infrastructure.processing_time(source_node, dest_node),
            hops=path,
        )

    async def get_neighbors(self, application_id: str, service_id: str) -> list[str]:
        """Returns the logical neighbors of a service in an application.

        Args:
            application_id (str): The ID of the application.
            service_id (str): The ID of the service for which to retrieve the neighbors.

        Returns:
            list[str]: A list of service IDs.
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
