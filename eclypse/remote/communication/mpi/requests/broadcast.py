"""Module for the BroadcastRequest class, subclassing MulticastRequest.

It represents a request to broadcast a message to all neighbor services in the network.
"""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
)

from eclypse.remote import ray_backend

from .multicast import MulticastRequest

if TYPE_CHECKING:
    from collections.abc import (
        Generator,
    )
    from datetime import datetime

    from eclypse.remote.communication.mpi import EclypseMPI


class BroadcastRequest(MulticastRequest):
    """Request for broadcasting a message to all neighbor services in the network."""

    def __init__(
        self,
        body: dict[str, Any],
        _mpi: EclypseMPI,
        timestamp: datetime | None = None,
    ):
        """Initializes a BroadcastRequest object.

        Args:
            body (dict[str, Any]): The body of the request.
            _mpi (EclypseMPI): The MPI interface.
            timestamp (datetime | None, optional): The timestamp of the request.
                Defaults to None.
        """
        super().__init__(
            recipient_ids=ray_backend.get(_mpi.get_neighbors()),
            body=body,
            _mpi=_mpi,
            timestamp=timestamp,
        )

    def __await__(self) -> Generator[Any, None, BroadcastRequest]:
        """Await the request to complete.

        Returns:
            Awaitable: The result of the request.
        """
        return super().__await__()  # type: ignore[return-value]
