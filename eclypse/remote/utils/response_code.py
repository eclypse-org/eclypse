"""Module for the ResponseCode enumeration.

It defines the possible responses to an EclypseRequest.
"""

from enum import (
    Enum,
    auto,
)


class ResponseCode(Enum):
    """Enum class, denoting possible responses to an `EclypseRequest`.

    Attributes:
        OK: The request was processed successfully.
        ERROR: An error occurred while processing the request.
    """

    OK = auto()
    ERROR = auto()
