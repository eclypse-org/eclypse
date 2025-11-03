"""Module for an integer enumeration for HTTP status codes."""

from enum import IntEnum


class HTTPStatusCode(IntEnum):
    """HTTP status codes used by the `EclypseREST` communication interface.

    Attributes:
        OK: 200 - OK status code.
        CREATED: 201 - Created status code.
        NO_CONTENT: 204 - No Content status code.
        BAD_REQUEST: 400 - Bad Request status code.
        UNAUTHORIZED: 401 - Unauthorized status code.
        FORBIDDEN: 403 - Forbidden status code.
        NOT_FOUND: 404 - Not Found status code.
        METHOD_NOT_ALLOWED: 405 - Method Not Allowed status code.
        CONFLICT: 409 - Conflict status code.
        INTERNAL_SERVER_ERROR: 500 - Internal Server Error status code.
        NOT_IMPLEMENTED: 501 - Not Implemented status code.
        SERVICE_UNAVAILABLE: 503 - Service Unavailable status code.
        GATEWAY_TIMEOUT: 504 - Gateway Timeout status code.
    """

    OK = 200
    CREATED = 201
    NO_CONTENT = 204
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    CONFLICT = 409
    INTERNAL_SERVER_ERROR = 500
    NOT_IMPLEMENTED = 501
    SERVICE_UNAVAILABLE = 503
    GATEWAY_TIMEOUT = 504
