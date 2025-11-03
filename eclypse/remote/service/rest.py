"""Module for the RESTService class.

It uses the REST interface to communicate with other services in the same application.

It differs from a base Service, since it runs its own loop forever, handling the
communication with other services through HTTP requests.
"""

from __future__ import annotations

from .service import Service


class RESTService(Service):
    """Base class for services in ECLYPSE remote applications."""

    def __init__(
        self,
        service_id: str,
    ):
        """Initializes a Service object.

        Args:
            service_id (str): The name of the service.
        """
        super().__init__(service_id=service_id, comm_interface="rest")

    async def step(self):
        """The service's main loop.

        This method must be overridden by the user.

        Returns:
            Any: The result of the step (if any).
        """

    def _init_thread(self):
        self._run_task_fn = lambda: None
        super()._init_thread()

    def _stop(self):
        """Stops the service."""
        if not self.deployed:
            raise RuntimeError(f"Service {self.id} is not deployed on any node.")
        if self.running:
            self._running = False
            self._loop.call_soon_threadsafe(self._loop.stop)
            self._thread.join()

    @property
    def mpi(self):
        """Raises an error since the service is not an MPI service.

        Raises:
            RuntimeError: The service is not an MPI service.
        """
        raise RuntimeError(
            f"Service {self.id} implements {self._comm_interface}, not mpi."
        )
