"""Package for the REST communication interface, based on the REpresentational State
Transfer (REST) protocol."""

from .interface import EclypseREST, register_endpoint as endpoint
from .codes import HTTPStatusCode
from .methods import HTTPMethod

__all__ = ["EclypseREST", "HTTPMethod", "HTTPStatusCode", "endpoint"]
