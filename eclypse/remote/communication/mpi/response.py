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

    A Response is a data structure for acknowledging the processing of a message
    exchange within an `MPIRequest`.
    """

    code: ResponseCode = ResponseCode.OK
    """The response code describing the message-processing outcome."""

    timestamp: datetime = field(default_factory=datetime.now)
    """The timestamp when the response object was created."""

    def __str__(self) -> str:
        """Returns a string representation of the response.

        Returns:
            str: The string representation of the response, in the format:
                <timestamp> - <code>
        """
        return f"{self.timestamp} - {self.code}"

    def __repr__(self) -> str:
        """Returns the official string representation of the response.

        Returns:
            str: The string representation of the response, same as __str__.
        """
        return self.__str__()
