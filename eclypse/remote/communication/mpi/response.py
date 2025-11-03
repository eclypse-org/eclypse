"""Module for the Response class.

It is used to acknowledge the processing of a message exchange within an MPIRequest.
"""

from datetime import datetime
from typing import Optional

from eclypse.remote.utils import ResponseCode


class Response:
    """Response class.

    A Response is a data structure for acknowledging the processing of a message
    exchange within an `MPIRequest`.
    """

    def __init__(
        self,
        code: ResponseCode = ResponseCode.OK,
        timestamp: Optional[datetime] = None,
    ):
        """Initializes a Response object.

        Args:
            code (ResponseCode): The response code.
            timestamp (datetime.datetime): The timestamp of the response.
        """
        self.code = code
        self.timestamp = timestamp if timestamp is not None else datetime.now()

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
