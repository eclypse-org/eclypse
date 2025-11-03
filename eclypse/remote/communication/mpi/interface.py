"""Module for the EclypseMPI class.

It implements the MPI communication protocol among services in the same application.
"""

from __future__ import annotations

import inspect
from asyncio import Queue
from datetime import datetime
from typing import (
    TYPE_CHECKING,
    Any,
    Coroutine,
    Dict,
    List,
    Optional,
    Union,
)

from eclypse.remote.communication.interface import (
    EclypseCommunicationInterface,
)
from eclypse.remote.utils import ResponseCode

from .requests import (
    BroadcastRequest,
    MulticastRequest,
    UnicastRequest,
)
from .response import Response

if TYPE_CHECKING:
    from eclypse.remote.communication import Route
    from eclypse.remote.service import Service


class EclypseMPI(EclypseCommunicationInterface):
    """EclypseMPI class.

    It implements the MPI communication protocol among services in the
    same application, deployed within the same infrastructure.

    It allows to send and receive messages among services, and to broadcast messages as
    well. The protocol is implemented by using the `MPIRequest` objects, which employ
    asynchrony to handle the simulation of communication costs of interactions.
    """

    def __init__(self, service: Service):
        """Initializes the MPI interface.

        Args:
            service (Service): The service that uses the MPI interface.
        """
        super().__init__(service)
        self._input_queue: Queue = Queue()

    def send(
        self,
        recipient_ids: Union[str, List[str]],
        body: Dict[str, Any],
        timestamp: Optional[datetime] = None,
    ) -> Union[UnicastRequest, MulticastRequest]:
        """Sends a message to a single recipient or multiple recipients.

        When awaited, the total wait time is the communication cost between the sender and the
        recipient in the case of a unicast, and the maximum communication cost among the
        interactions with the recipients in the case of a multicast. The result of this
        method **must be awaited**.

        Args:
            recipient_ids (Union[str, List[str], None]): The ids of the recipients. If a \
                single id is specified, the message is sent to a single recipient. If a \
                list of ids is specified, the message is sent to multiple recipients.
            body (Dict[str, Any]): The data to be sent. It must be a pickleable object.
            timestamp (Optional[datetime.datetime], optional): The timestamp of the \
                message. Defaults to datetime.datetime.now().

        Returns:
            Union[UnicastRequest, MulticastRequest]: The MPI request.
        """
        if not timestamp:
            timestamp = datetime.now()

        if not isinstance(body, dict):
            raise ValueError("body must be a dictionary")

        if isinstance(recipient_ids, str):
            return UnicastRequest(recipient_ids, body=body, _mpi=self)
        if isinstance(recipient_ids, list):
            return MulticastRequest(recipient_ids, body=body, _mpi=self)

        raise ValueError("recipient_ids must be a string or a list of strings")

    def bcast(
        self,
        body: Any,
        timestamp: Optional[datetime] = None,
    ) -> BroadcastRequest:
        """Broadcasts a message to all neighbor services.

        When awaited, the total wait time is the maximum communication cost
        among the interactions with neighbors. The result of this method **must be awaited**.

        Args:
            body (Any): The data to be sent. It must be a pickleable object.
            timestamp (Optional[datetime.datetime], optional): The timestamp of the \
                message. Defaults to datetime.datetime.now().

        Returns:
            BroadcastRequest: The Broadcast MPI request.
        """
        if not isinstance(body, dict):
            raise ValueError("body must be a dictionary")

        return BroadcastRequest(body=body, _mpi=self, timestamp=timestamp)

    def recv(self) -> Coroutine[Any, Any, Dict[str, Any]]:
        """Receive a message in the input queue.

        The result of this method **must be awaited**.

        Returns:
            Task[Any]: The message in the input queue.
        """
        return self._input_queue.get()

    async def _not_connected_response(self) -> Any:
        return Response(ResponseCode.ERROR)

    async def _execute_request(  # pylint: disable=arguments-differ
        self, route: Route, **body
    ) -> Response:
        body["sender_id"] = route.sender_id
        await self._input_queue.put(body)
        return Response()


def exchange(
    *,
    receive: bool = False,
    send: bool = False,
    broadcast: bool = False,
):
    """Decorator to require and send a message in a Service method.

    The decorated function must receive, send, or broadcast a message.
    Sending and broadcasting are mutually exclusive.

    Args:
        receive (bool, optional): True if the decorated function receives a message. \
            Defaults to False.
        send (bool, optional): True if the decorated function sends a message. \
            Defaults to False.
        broadcast (bool, optional): True if the decorated function broadcasts a message.\
            Defaults to False.
    """
    if send and broadcast:
        raise ValueError(
            "The decorated function cannot send and broadcast at the same time"
        )

    if not send and not broadcast and not receive:
        raise ValueError(
            "The decorated function must send, broadcast, or receive a message"
        )

    def decorator(func):
        async def wrapper(self: Service, *args, **kwargs):
            if receive:
                message = await self.mpi.recv()
                sender_id: str = message.pop("sender_id")
                # add message to args
                args = (sender_id, message, *args)

            if inspect.iscoroutinefunction(func):
                next_args = await func(self, *args, **kwargs)
            else:
                next_args = func(self, *args, **kwargs)

            if send:
                return self.mpi.send(*next_args)
            if broadcast:
                return self.mpi.bcast(next_args)
            return next_args

        return wrapper

    return decorator
