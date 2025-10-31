# pylint: disable=protected-access
"""Module for Request class, which is the unit of communication between services."""

from __future__ import annotations

import asyncio
from datetime import datetime
from functools import cached_property
from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Generator,
    List,
    Optional,
    Union,
)

from eclypse.remote import ray_backend

if TYPE_CHECKING:
    from asyncio import Future
    from datetime import timedelta

    from ray import ObjectRef

    from eclypse.remote._node import RemoteNode

    from .interface import EclypseCommunicationInterface
    from .route import Route


class EclypseRequest:
    """Class for an Eclypse request."""

    def __init__(
        self,
        recipient_ids: List[str],
        data: Dict[str, Any],
        _comm: EclypseCommunicationInterface,
        timestamp: Optional[datetime] = None,
    ):
        """Create a new EclypseRequest.

        Args:
            recipient_ids (List[str]): The ids of the recipients.
            data (Dict[str, Any]): The data of the request.
            _comm (EclypseCommunicationInterface): The communication interface.
            timestamp (Optional[datetime], optional): The timestamp of the request.
                Defaults to None.
        """
        self._data = data
        self._timestamp = timestamp if timestamp is not None else datetime.now()

        self._recipient_ids: List[str] = recipient_ids
        self._routes: List[Future[Route]] = [
            asyncio.wrap_future(
                _comm.request_route(recipient_id).future(),  # type: ignore[attr-defined]
                loop=_comm.service._node.engine_loop,  # type: ignore[union-attr]
            )
            for recipient_id in self._recipient_ids
        ]

        self._futures = [
            asyncio.wrap_future(
                asyncio.run_coroutine_threadsafe(
                    _process_request(
                        self.data, self._ref_args, route, recipient_id, _comm
                    ),
                    loop=_comm.service._node.engine_loop,  # type: ignore[union-attr]
                )
            )
            for route, recipient_id in zip(
                self._routes, self._recipient_ids, strict=False
            )
        ]

    def __await__(self) -> Generator[Any, None, EclypseRequest]:
        """Await the request to complete.

        Returns:
            Awaitable: The result of the request.
        """

        async def wrapper(obj: EclypseRequest) -> EclypseRequest:
            await asyncio.gather(*obj._futures)  # pylint: disable=protected-access
            return obj

        return wrapper(self).__await__()

    @property
    def data(self) -> Dict[str, Any]:
        """Get the data of the request.

        Returns:
            Dict[str, Any]: The data.
        """
        return self._data

    @property
    def timestamp(self) -> datetime:
        """Get the timestamp of the request.

        Returns:
            datetime: The timestamp.
        """
        return self._timestamp

    @property
    def recipient_ids(self) -> List[str]:
        """The ids of the recipients.

        Returns:
            List[str]: The ids.
        """
        return self._recipient_ids

    @property
    def routes(self) -> List[Optional[Route]]:
        """Wait for the routes to be computed.

        This method can be awaited explicitly to
        compute the routes to the recipients. Otherwise, it is awaited implicitly when
        the `EclypseRequest` object is awaited to process the request.
        """
        return [(r.result() if r.done() else None) for r in self._routes]

    @property
    def responses(self) -> List[Optional[Any]]:
        """Wait for the responses to the MPI request.

        This method can be called explicitly to wait for the responses to the EclypseRequest
        Otherwise, it is called implicitly when the `EclypseRequest` object is awaited to
        process the request.
        """
        return [(f.result()["future"] if f.done() else None) for f in self._futures]

    @property
    def elapsed_times(self) -> List[Optional[timedelta]]:
        """The elapsed times until the responses were received.

        Returns:
            List[timedelta]: The elapsed times until the responses were received.
                If a response is not yet available, a timedelta of 0 is returned
                for the corresponding recipient.
        """
        times: List[Optional[timedelta]] = []
        for r in self._futures:
            if r.done():
                times.append(r.result()["timestamp"] - self.timestamp)
            else:
                times.append(None)
        return times

    @cached_property
    def _ref_args(self) -> Dict[str, ObjectRef]:
        return {k: ray_backend.put(v) for k, v in self.data.items()}


async def _process_request(
    args: Dict[str, Any],
    args_ref: Dict[str, ObjectRef],
    route: Future[Route],
    recipient_id: str,
    _comm: EclypseCommunicationInterface,
) -> Dict[str, Union[Any, datetime]]:
    _route = route.result() if route.done() else await route
    if _route is None:
        raise RuntimeError(f"Route to {recipient_id} not found")

    if _route.no_hop:
        future = _comm.service._node.service_comm_entrypoint(  # type: ignore[union-attr]
            _route,
            _comm.__class__,
            **args,
        )
    else:
        infrastructure_id = _comm.service._node.infrastructure_id  # type: ignore[union-attr]
        handle: RemoteNode = ray_backend.get_actor(
            f"{infrastructure_id}/{_route.recipient_node_id}"
        )
        await asyncio.sleep(_route.cost(args))
        future = handle.service_comm_entrypoint.remote(  # type: ignore[attr-defined]
            _route,
            _comm.__class__,
            **args_ref,
        )
    return {"future": await future, "timestamp": datetime.now()}
