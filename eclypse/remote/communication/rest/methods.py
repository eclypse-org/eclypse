"""Module for the HTTPMethod class.

It defines the http metohds supported by the `EclypseREST` communication interface.
"""

from enum import StrEnum


class HTTPMethod(StrEnum):
    """HTTP methods supported by the `EclypseREST` communication interface."""

    GET = "GET"
    """The HTTP GET method."""

    POST = "POST"
    """The HTTP POST method."""

    PUT = "PUT"
    """The HTTP PUT method."""

    DELETE = "DELETE"
    """The HTTP DELETE method."""
