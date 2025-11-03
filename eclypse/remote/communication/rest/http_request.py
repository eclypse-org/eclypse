"""Module for the HTTPRequest class.

It is used to send and receive data between services that
communicate using the REST communication interface.
"""

from __future__ import annotations

from typing import (
    TYPE_CHECKING,
    Any,
    Dict,
    Generator,
    Optional,
    Tuple,
)

from eclypse.remote.communication import EclypseRequest

if TYPE_CHECKING:
    from eclypse.remote.communication import Route

    from .codes import HTTPStatusCode
    from .interface import EclypseREST
    from .methods import HTTPMethod


class HTTPRequest(EclypseRequest):
    """HTTPRequest class.

    An HTTP request is used to send and receive data between services in the
    same application, using the REST communication protocol.
    """

    def __init__(
        self,
        url: str,
        method: HTTPMethod,
        data: Dict[Any, Any],
        _rest: EclypseREST,
    ):
        """Initializes an HTTPRequest object.

        Args:
            url (str): The URL of the request.
            method (HTTPMethod): The HTTP method of the request.
            data (Dict[Any, Any]): The data to send in the request.
            _rest (EclypseREST): The REST interface used to send the request.
        """
        recipient_id = url.split("/")[0]
        data["url"] = url
        data["method"] = method

        super().__init__(
            recipient_ids=[recipient_id],
            data=data,
            _comm=_rest,
        )

    def __await__(self) -> Generator[Any, None, HTTPRequest]:
        """Await the request to complete.

        Returns:
            Awaitable: The result of the request.
        """
        return super().__await__()  # type: ignore[return-value]

    @property
    def route(self) -> Optional[Route]:
        """Get the route of the request.

        Returns:
            Optional[Route]: The route of the request.
        """
        return self.routes[0]

    @property
    def response(self) -> Optional[Tuple[HTTPStatusCode, Dict[str, Any]]]:
        """Get the response of the request.

        Returns:
            Tuple[HTTPStatusCode, Dict[str, Any]]: The response of the request.
        """
        return self.responses[0]

    @property
    def status_code(self) -> HTTPStatusCode:
        """Get the status code of the response.

        Returns:
            HTTPStatusCode: The status code of the response.

        Raises:
            RuntimeError: If the request is not completed yet.
        """
        if self.response is None:
            raise RuntimeError("Request not completed yet")
        return self.response[0]

    @property
    def body(self) -> Dict[str, Any]:
        """Get the body of the response.

        Returns:
            Dict[str, Any]: The body of the response.

        Raises:
            RuntimeError: If the request is not completed yet.
        """
        if self.response is None:
            raise RuntimeError("Request not completed yet")
        return self.response[1]
