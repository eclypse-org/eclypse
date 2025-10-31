"""Module for the Response class, used to acknowledge the processing of a message
exchange within an MPIRequest."""

from datetime import datetime

from eclypse.remote.utils import ResponseCode


class Response:
    """A Response is a data structure for acknowledging the processing of a message
    exchange within an `MPIRequest`."""

    def __init__(
        self,
        code: ResponseCode = ResponseCode.OK,
        timestamp: datetime = datetime.now(),
    ):
        """Initializes a Response object.

        Args:
            code (ResponseCode): The response code.
            timestamp (datetime.datetime): The timestamp of the response.
        """
        self.code = code
        self.timestamp = timestamp

    def __str__(self) -> str:
        """Returns a string representation of the response, with the format:
        <timestamp> - <code>

        Returns:
            str: The string representation of the response.
        """
        return f"{self.timestamp} - {self.code}"

    def __repr__(self) -> str:
        """Returns a string representation of the response, with the format:
        <timestamp> - <code>

        Returns:
            str: The string representation of the response.
        """
        return self.__str__()
