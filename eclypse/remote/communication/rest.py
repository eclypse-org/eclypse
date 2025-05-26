"""Package for the REST communication interface, based on the REpresentational State
Transfer (REST) protocol.

For the complete documentation, refer to the :py:mod:`~eclypse_core.remote.communication.rest`
core package.
"""

from eclypse_core.remote.communication.rest import (
    EclypseREST,
    HTTPMethod,
    HTTPStatusCode,
    endpoint,
)

__all__ = [
    "EclypseREST",
    "HTTPMethod",
    "HTTPStatusCode",
    "endpoint",
]
