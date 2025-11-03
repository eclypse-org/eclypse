"""Package for the REST communication interface.

Based on the
`Representational State Transfer (REST) protocol <https://it.wikipedia.org/wiki/Representational_state_transfer>`_.
"""

from .interface import EclypseREST, register_endpoint as endpoint
from .codes import HTTPStatusCode
from .methods import HTTPMethod

__all__ = ["EclypseREST", "HTTPMethod", "HTTPStatusCode", "endpoint"]
