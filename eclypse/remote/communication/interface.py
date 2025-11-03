"""Module for the EclypseCommunicationInterface class.

It contains the implementation of the interface used by services to communicate.
"""

from __future__ import annotations

import asyncio
from typing import (
    TYPE_CHECKING,
    Any,
    Coroutine,
    List,
    Optional,
    Union,
)

from eclypse.remote import ray_backend

if TYPE_CHECKING:
    from asyncio import (
        Future,
        Task,
    )

    from eclypse.remote.service import Service
    from eclypse.simulation._simulator.remote import RemoteSimulator

    from .route import Route


class EclypseCommunicationInterface:
    """EclypseCommunicationInterface class.

    It is used to implement and simulate the interactions between services deployed
    and running in the same infrastructure.

    It allows to interact with the `RemoteSimulator`, which provides the details regarding
    the current state of the infrastructure, and simulate the behaviour of the services
    accordingly.
    """

    def __init__(self, service: Service):
        """Initializes the communication interface.

        Args:
            service (Service): The service that uses the communication interface.
        """
        self._service: Service = service
        self._im: Optional[RemoteSimulator] = None

    def connect(self):
        """Connects the communication interface to the `RemoteSimulator`."""
        self._im = ray_backend.get_actor(
            name=f"{self._service._node.infrastructure_id}/manager"  # pylint: disable=protected-access
        )

    def disconnect(self):
        """Disconnects the communication interface from the `RemoteSimulator`."""
        self._im = None

    def request_route(self, recipient_id: str) -> Future[Route]:
        """Interacts with the `RemoteSimulator` to request a route to a desired recipient service.

        The result of the function can be obtained by calling
        `ray.get` or by awaiting it.

        Args:
            recipient_id (str): The ID of the recipient service.

        Returns:
            Task[Route]: The route to the recipient service.
        """
        if self._im:
            return self._im.route.remote(  # type: ignore[attr-defined]
                self.service.application_id,
                self.service.id,
                recipient_id,
            )
        raise ValueError(
            "The communication interface is not connected to the RemoteSimulator."
        )

    def get_neighbors(self) -> Task[List[str]]:
        """Interacts with the InfrastructureManager to request the list of service neighbors.

        The result of the function can be obtained by calling `ray.get` or by awaiting it.

        Returns:
            Task[List[str]]: The list of neighbor service IDs.
        """
        if self._im:
            return self._im.get_neighbors.remote(  # type: ignore[attr-defined]
                self.service.application_id,
                self.service.id,
            )
        raise ValueError(
            "The communication interface is not connected to the RemoteSimulator."
        )

    def _handle_request(
        self, *args, **kwargs
    ) -> Union[Coroutine[Any, Any, Any], Future[Any]]:
        """Enqueue a message in the input queue.

        This method is called internally by the communication interface.

        Args:
            *args: The arguments of the request.
            **kwargs: The keyword arguments of the request.
        """
        if not self.connected:
            return self._not_connected_response()

        return asyncio.wrap_future(
            asyncio.run_coroutine_threadsafe(
                self._execute_request(*args, **kwargs),
                self.service.event_loop,
            )
        )

    async def _not_connected_response(self) -> Any:
        """Returns the response when the communication interface is not connected.

        Returns:
            Any: The response.

        Raises:
            NotImplementedError: The method is not implemented.
        """
        raise NotImplementedError

    async def _execute_request(self, *args, **kwargs) -> Any:
        """Enqueue a message in the input queue.

        This method is called internally by the communication interface.

        Args:
            *args: The arguments of the request.
            **kwargs: The keyword arguments of the request.

        Returns:
            Any: The response.
        """
        raise NotImplementedError

    @property
    def connected(self) -> bool:
        """Returns True if the communication interface is connected to the RemoteSimulator.

        Returns:
            bool: True if the communication interface is connected.
        """
        return self._im is not None

    @property
    def service(self) -> Service:
        """Returns the service leveraging the communication interface.

        Returns:
            Service: The service leveraging the communication interface.
        """
        return self._service
