"""Package for classes allowing the definition of logic for services in ECLYPSE remote
simulations."""

from .service import Service
from .rest import RESTService

__all__ = ["RESTService", "Service"]
