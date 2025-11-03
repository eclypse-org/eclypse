"""Module for the BroadcastRequest class, subclassing MulticastRequest.

It represents a request to broadcast a message to all neighbor services in the network.
"""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Generator,
    Optional,
)

from eclypse.remote import ray_backend

from .multicast import MulticastRequest

if TYPE_CHECKING:
    from datetime import datetime

    from eclypse.remote.communication.mpi import EclypseMPI


class BroadcastRequest(MulticastRequest):
    """Request for broadcasting a message to all neighbor services in the network."""

    def __init__(
        self,
        body: Dict[str, Any],
        _mpi: EclypseMPI,
        timestamp: Optional[datetime] = None,
    ):
        """Initializes a BroadcastRequest object.

        Args:
            body (Dict[str, Any]): The body of the request.
            _mpi (EclypseMPI): The MPI interface.
            timestamp (Optional[datetime], optional): The timestamp of the request.
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
