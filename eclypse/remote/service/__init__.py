"""Package for classes defining service logic in ECLYPSE remote simulations."""

from .service import Service
from .rest import RESTService

__all__ = ["RESTService", "Service"]
