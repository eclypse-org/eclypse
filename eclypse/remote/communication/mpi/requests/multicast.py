"""Module for the MulticastRequest class, subclassing MPIRequest.

It represents a request to send a message to multiple recipients.
"""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Generator,
    List,
    Optional,
)

from eclypse.remote.communication import EclypseRequest

if TYPE_CHECKING:
    from datetime import datetime

    from eclypse.remote.communication.mpi import EclypseMPI


class MulticastRequest(EclypseRequest):
    """A request to send a message to multiple recipients."""

    def __init__(
        self,
        recipient_ids: List[str],
        body: Dict[str, Any],
        _mpi: EclypseMPI,
        timestamp: Optional[datetime] = None,
    ):
        """Initializes a MulticastRequest object.

        Args:
            recipient_ids (List[str]): The IDs of the recipient nodes.
            body (Dict[str, Any]): The body of the request.
            _mpi (EclypseMPI): The MPI interface.
            timestamp (Optional[datetime], optional): The timestamp of the request.
                Defaults to None.
        """
        super().__init__(
            recipient_ids=recipient_ids,
            data=body,
            _comm=_mpi,
            timestamp=timestamp,
        )

    def __await__(self) -> Generator[Any, None, MulticastRequest]:
        """Await the request to complete.

        Returns:
            Awaitable: The result of the request.
        """
        return super().__await__()  # type: ignore[return-value]
