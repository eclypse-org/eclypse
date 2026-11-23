# pylint: disable=protected-access
"""Module for Request class, which is the unit of communication between services."""

from __future__ import annotations

import asyncio
from datetime import datetime
from functools import cached_property
from typing import (
    TYPE_CHECKING,
    Any,
)

from eclypse.remote import ray_backend

if TYPE_CHECKING:
    from asyncio import Future
    from collections.abc import (
        Generator,
    )
    from datetime import timedelta

    from ray import ObjectRef

    from eclypse.remote.node import RemoteNode

    from .interface import EclypseCommunicationInterface
    from .route import Route


class EclypseRequest:
    """Class for an Eclypse request."""

    def __init__(
        self,
        recipient_ids: list[str],
        data: dict[str, Any],
        _comm: EclypseCommunicationInterface,
        timestamp: datetime | None = None,
    ):
        """Create a new EclypseRequest.

        Args:
            recipient_ids (list[str]): The ids of the recipients.
            data (dict[str, Any]): The data of the request.
            _comm (EclypseCommunicationInterface): The communication interface.
            timestamp (datetime | None, optional): The timestamp of the request.
                Defaults to None.
        """
        self._data = data
        self._timestamp = timestamp or datetime.now()

        self._recipient_ids: list[str] = recipient_ids
        self._routes: list[Future[Route | None]] = [
            asyncio.wrap_future(
                _comm.request_route(recipient_id).future(),  # type: ignore[attr-defined]
                loop=_comm.service.node.engine_loop,
            )
            for recipient_id in self._recipient_ids
        ]

        self._futures = [
            asyncio.wrap_future(
                asyncio.run_coroutine_threadsafe(
                    _process_request(
                        self._ref_args,
                        self._size,
                        route,
                        recipient_id,
                        _comm,
                    ),
                    loop=_comm.service.node.engine_loop,
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
    def data(self) -> dict[str, Any]:
        """Get the data of the request.

        Returns:
            dict[str, Any]: The data.
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
    def recipient_ids(self) -> list[str]:
        """The ids of the recipients.

        Returns:
            list[str]: The ids.
        """
        return self._recipient_ids

    @property
    def routes(self) -> list[Route | None]:
        """Wait for the routes to be computed.

        This method can be awaited explicitly to compute the routes to the recipients.
        Otherwise, it is awaited implicitly when the `EclypseRequest` object is awaited
        to process the request.
        """
        return [(r.result() if r.done() else None) for r in self._routes]

    @property
    def responses(self) -> list[Any | None]:
        """Wait for the responses to the MPI request.

        This method can be called explicitly to wait for the responses to the
        EclypseRequest. Otherwise, it is called implicitly when the `EclypseRequest`
        object is awaited to process the request.
        """
        return [(f.result()["future"] if f.done() else None) for f in self._futures]

    @property
    def elapsed_times(self) -> list[timedelta | None]:
        """The elapsed times until the responses were received.

        Returns:
            list[timedelta]: The elapsed times until the responses were received.
                If a response is not yet available, a timedelta of 0 is returned
                for the corresponding recipient.
        """
        times: list[timedelta | None] = []
        for r in self._futures:
            if r.done():
                times.append(r.result()["timestamp"] - self.timestamp)
            else:
                times.append(None)
        return times

    @cached_property
    def _ref_args(self) -> dict[str, ObjectRef]:
        return {k: ray_backend.put(v) for k, v in self.data.items()}

    @cached_property
    def _size(self) -> int:
        return ray_backend.get_size(list(self._ref_args.values()))


async def _process_request(
    args_ref: dict[str, ObjectRef],
    msg_size: int,
    route: Future[Route | None],
    recipient_id: str,
    _comm: EclypseCommunicationInterface,
) -> dict[str, Any | datetime]:
    _route = route.result() if route.done() else await route
    if _route is None:
        return {
            "future": _comm._route_not_found_response(recipient_id),
            "timestamp": datetime.now(),
        }

    if _route.no_hop:
        # Read back from the object store, so delivery does not depend on placement
        args = {k: await ref for k, ref in args_ref.items()}
        future = _comm.service.node.service_comm_entrypoint(
            _route,
            _comm.__class__,
            **args,
        )
        response = await future
    else:
        from ray.exceptions import (  # noqa: PLC0415 -- Ray is optional until delivery.
            ActorDiedError,
            ActorUnavailableError,
        )

        infrastructure_id = _comm.service.infrastructure_id
        actor_name = f"{infrastructure_id}/{_route.recipient_node_id}"
        try:
            handle: RemoteNode = _comm.service.node.get_actor(actor_name)
        except ValueError as error:
            return {
                "future": _comm._recipient_unavailable_response(recipient_id, error),
                "timestamp": datetime.now(),
            }
        await asyncio.sleep(_route.cost(msg_size))
        try:
            future = handle.service_comm_entrypoint.remote(  # type: ignore[attr-defined]
                _route,
                _comm.__class__,
                **args_ref,
            )
            response = await future
        except (ActorDiedError, ActorUnavailableError) as error:
            response = _comm._recipient_unavailable_response(recipient_id, error)
    return {"future": response, "timestamp": datetime.now()}
