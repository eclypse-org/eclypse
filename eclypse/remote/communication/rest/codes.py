"""Module for an integer enumeration for HTTP status codes."""

from enum import IntEnum


class HTTPStatusCode(IntEnum):
    """HTTP status codes used by the `EclypseREST` communication interface."""

    OK = 200
    """The request has succeeded."""

    CREATED = 201
    """The request has been fulfilled and a new resource has been created."""

    NO_CONTENT = 204
    """The request has succeeded and there is no content to return."""

    BAD_REQUEST = 400
    """The request could not be understood by the server."""

    UNAUTHORIZED = 401
    """The request requires valid authentication credentials."""

    FORBIDDEN = 403
    """The server understood the request but refuses to authorise it."""

    NOT_FOUND = 404
    """The requested resource could not be found."""

    METHOD_NOT_ALLOWED = 405
    """The request method is not allowed for the target resource."""

    CONFLICT = 409
    """The request conflicts with the current state of the resource."""

    INTERNAL_SERVER_ERROR = 500
    """The server encountered an unexpected condition."""

    NOT_IMPLEMENTED = 501
    """The server does not support the functionality required to fulfil the request."""

    SERVICE_UNAVAILABLE = 503
    """The server is temporarily unable to handle the request."""

    GATEWAY_TIMEOUT = 504
    """The server did not receive a timely response from an upstream server."""
