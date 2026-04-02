"""Module for the ResponseCode enumeration.

It defines the possible responses to an EclypseRequest.
"""

from enum import (
    Enum,
    auto,
)


class ResponseCode(Enum):
    """Enum class, denoting possible responses to an `EclypseRequest`."""

    OK = auto()
    """The request was processed successfully."""

    ERROR = auto()
    """An error occurred while processing the request."""
