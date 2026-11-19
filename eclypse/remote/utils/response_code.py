"""Module for the ResponseCode enumeration.

It defines outcomes for MPI delivery and remote lifecycle operations.
"""

from enum import (
    Enum,
    auto,
)


class ResponseCode(Enum):
    """Outcomes for MPI delivery and remote lifecycle operations."""

    OK = auto()
    """The operation succeeded, or the MPI message was queued."""

    ERROR = auto()
    """An error occurred while processing the request."""

    NOT_CONNECTED = auto()
    """The recipient's MPI interface is disconnected."""

    ROUTE_NOT_FOUND = auto()
    """No usable route to the recipient was found."""

    RECIPIENT_UNAVAILABLE = auto()
    """The recipient service or actor became unavailable during delivery."""
