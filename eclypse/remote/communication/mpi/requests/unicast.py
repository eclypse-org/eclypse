"""Module for UnicastRequest class, subclassing MPIRequest.

It represents a request to send a message to a single recipient.
"""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
)

from eclypse.remote.communication.mpi.requests import MulticastRequest

if TYPE_CHECKING:
    from collections.abc import (
        Generator,
    )
    from datetime import (
        datetime,
        timedelta,
    )

    from eclypse.remote.communication.mpi import (
        EclypseMPI,
        Response,
    )
    from eclypse.remote.communication.route import Route


class UnicastRequest(MulticastRequest):
    """A request to send a message to a single recipient."""

    def __init__(
        self,
        recipient_id: str,
        body: dict[str, Any],
        _mpi: EclypseMPI,
        timestamp: datetime | None = None,
    ):
        """Initializes a UnicastRequest object.

        Args:
            recipient_id (str): The ID of the recipient node.
            body (dict[str, Any]): The body of the request.
            _mpi (EclypseMPI): The MPI interface.
            timestamp (datetime | None, optional): The timestamp of the request.
                Defaults to None.
        """
        super().__init__(
            recipient_ids=[recipient_id],
            body=body,
            _mpi=_mpi,
            timestamp=timestamp,
        )

    def __await__(self) -> Generator[Any, None, UnicastRequest]:
        """Await the request to complete.

        Returns:
            Awaitable: The result of the request.
        """
        return super().__await__()  # type: ignore[return-value]

    @property
    def recipient_id(self) -> str:
        """The ID of the recipient.

        Returns:
            str: The ID.
        """
        return self._recipient_ids[0]

    @property
    def response(self) -> Response | None:
        """The response to the request.

        Returns:
            Response | None: The response to the request if available, None otherwise.
        """
        return self.responses[0]

    @property
    def route(self) -> Route | None:
        """The route to the recipient.

        Returns:
            Route | None: The route to the recipient if available, None otherwise.
        """
        return self.routes[0]

    @property
    def elapsed_time(self) -> timedelta | None:
        """The elapsed time until the response was received.

        Returns:
            timedelta | None: The elapsed time until the response was received,
                or None if the response is not yet available.
        """
        return self.elapsed_times[0]
