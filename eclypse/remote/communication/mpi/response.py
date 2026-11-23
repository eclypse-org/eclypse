"""Module for the Response class.

It is used to acknowledge the processing of a message exchange within an MPIRequest.
"""

from dataclasses import (
    dataclass,
    field,
)
from datetime import datetime

from eclypse.remote.utils import ResponseCode


@dataclass(slots=True)
class Response:
    """Response class.

    A Response acknowledges an MPI delivery attempt. OK means the message was
    queued, not that the recipient finished processing it.
    """

    code: ResponseCode = ResponseCode.OK
    """The response code describing the message-processing outcome."""

    timestamp: datetime = field(default_factory=datetime.now)
    """The timestamp when the response object was created."""

    message: str | None = field(default=None, kw_only=True)
    """Diagnostic information about the delivery outcome."""

    def __str__(self) -> str:
        """Returns a string representation of the response.

        Returns:
            str: The string representation of the response, in the format:
                <timestamp> - <code>[: <message>]
        """
        result = f"{self.timestamp} - {self.code}"
        return f"{result}: {self.message}" if self.message else result

    def __repr__(self) -> str:
        """Returns the official string representation of the response.

        Returns:
            str: The string representation of the response, same as __str__.
        """
        return self.__str__()
