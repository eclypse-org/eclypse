"""Module for the EclypseREST class.

It implements the REST communication protocol among services in the same application.

It allows to send and receive HTTP requests at specific endpoints, which are defined by
each service, using the @endpoint decorator.
"""

from __future__ import annotations

import asyncio
import inspect
from collections import defaultdict
from typing import (
    TYPE_CHECKING,
    Any,
    Callable,
    Coroutine,
    Dict,
    Tuple,
    Union,
)

from eclypse.remote.communication.interface import (
    EclypseCommunicationInterface,
)
from eclypse.remote.communication.rest.http_request import HTTPRequest

from .codes import HTTPStatusCode
from .methods import HTTPMethod

if TYPE_CHECKING:
    from eclypse.remote.communication.route import Route
    from eclypse.remote.service import Service
    from eclypse.utils.types import HTTPMethodLiteral


class EclypseREST(EclypseCommunicationInterface):
    """EclypseREST class.

    It implements the REST communication interface among services in the
    same application, deployed within the same infrastructure.

    It allows to send and receive HTTP requests at specific endpoints, which are defined
    by each service, using the @endpoint decorator.
    """

    def __init__(self, service: Service):
        """Initializes the REST interface.

        Args:
            service (Service): The service that uses the REST interface.
        """
        super().__init__(service=service)
        self.endpoints: Dict[str, Dict[HTTPMethod, Callable]] = defaultdict(lambda: {})

    def connect(self):
        """Connects the REST interface to the service.

        It registers the endpoints and their handlers.
        """
        super().connect()
        for attr in dir(self.service):
            if attr == "mpi":
                continue
            fn = getattr(self.service, attr)
            if hasattr(fn, "__endpoint__"):
                endpoint = f"{self.service.id}{fn.__endpoint__}"
                method = fn.__method__
                if endpoint in self.endpoints and method in self.endpoints[endpoint]:
                    raise ValueError(f"{method} already registered for {endpoint}.")

                self.endpoints[endpoint][method] = fn

    def disconnect(self):
        """Disconnects the REST interface from the service, clearing the endpoints."""
        super().disconnect()
        self.endpoints.clear()

    def get(self, url: str, **data):
        """Creates and handles a GET request.

        Args:
            url (str): The URL of the request.
            **data: The data to be sent in the request.
        """
        return HTTPRequest(url, HTTPMethod.GET, data, self)

    def post(self, url: str, **data):
        """Creates and handles a POST request.

        Args:
            url (str): The URL of the request.
            **data: The data to be sent in the request.
        """
        return HTTPRequest(url, HTTPMethod.POST, data, self)

    def put(self, url: str, **data):
        """Creates and handles a PUT request.

        Args:
            url (str): The URL of the request.
            **data: The data to be sent in the request.
        """
        return HTTPRequest(url, HTTPMethod.PUT, data, self)

    def delete(self, url: str, **data):
        """Creates and handles a DELETE request.

        Args:
            url (str): The URL of the request.
            **data: The data to be sent in the request.
        """
        return HTTPRequest(url, HTTPMethod.DELETE, data, self)

    def _handle_request(
        self, *_, **kwargs
    ) -> Union[
        Coroutine[Any, Any, Any], asyncio.Future[Tuple[HTTPStatusCode, Dict[str, Any]]]
    ]:
        """Handles a request to an endpoint.

        Args:
            endpoint (str): The endpoint to handle.
            method (HTTPMethod): The method of the request.
            route (Route): The route of the request.
            *_: The positional arguments to be sent in the request.
            **kwargs: The data to be sent in the request.

        Returns:
            asyncio.Future[Tuple[HTTPStatusCode, Dict[str, Any]]]: The result of the \
                request, as a future.
        """
        if self.service._run_task is not None:  # pylint: disable=protected-access
            raise ValueError("Must use a RESTService to handle requests.")

        return super()._handle_request(**kwargs)

    async def _not_connected_response(self) -> Tuple[HTTPStatusCode, Dict[str, Any]]:
        """Returns a response when the service is not connected."""
        return HTTPStatusCode.INTERNAL_SERVER_ERROR, {
            "message": f"{self.service.id} not connected"
        }

    async def _execute_request(  # pylint: disable=arguments-differ
        self,
        url: str,
        method: HTTPMethod,
        route: Route,
        **kwargs,
    ) -> Tuple[HTTPStatusCode, Dict[str, Any]]:
        """Executes a request to an endpoint.

        Args:
            url (str): The URL of the request.
            endpoint (str): The endpoint to handle.
            method (HTTPMethod): The method of the request.
            route (Route): The route of the request.
            **kwargs: The data to be sent in the request.

        Returns:
            Tuple[HTTPStatusCode, Dict[str, Any]]: The result of the request.
        """
        if url not in self.endpoints:
            return HTTPStatusCode.NOT_FOUND, {"message": "Endpoint not found"}

        if method not in self.endpoints[url]:
            return HTTPStatusCode.METHOD_NOT_ALLOWED, {"message": "Method not allowed"}
        handler = self.endpoints[url][method]
        try:
            if inspect.iscoroutinefunction(handler):
                http_code, result = await handler(**kwargs)
            else:
                http_code, result = handler(**kwargs)
        except Exception as e:
            http_code, result = (
                HTTPStatusCode.INTERNAL_SERVER_ERROR,
                {"message": str(e)},
            )
        if not isinstance(result, dict):
            error_code = "Invalid return type for handler: data must be a dictionary."
            return HTTPStatusCode.INTERNAL_SERVER_ERROR, {"message": error_code}
        if http_code not in iter(HTTPStatusCode):
            error_code = "Invalid return type for handler: status code must be a valid HTTP code."
            return HTTPStatusCode.INTERNAL_SERVER_ERROR, {"message": error_code}

        if not isinstance(http_code, HTTPStatusCode):
            http_code = HTTPStatusCode(http_code)

        if not route.no_hop:
            await asyncio.sleep(route.cost((http_code, result)))

        return http_code, result


def register_endpoint(endpoint: str, method: Union[HTTPMethod, HTTPMethodLiteral]):
    """Decorator to register an endpoint in a service.

    Args:
        endpoint (str): The endpoint to register.
        method (Union[HTTPMethod, HTTPMethodLiteral]): The method allowed for the endpoint.

    Returns:
        Callable: The decorated function.
    """

    def decorator(func):
        _method = HTTPMethod[method] if not isinstance(method, HTTPMethod) else method

        func.__endpoint__ = endpoint
        func.__method__ = _method
        return func

    return decorator
