"""Package for classes allowing the definition of services logic in ECLYPSE remote simulations."""

from .service import Service
from .rest import RESTService

__all__ = ["RESTService", "Service"]
