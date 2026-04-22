"""DeathStarBench application builders (e.g. hotel reservation, social network).

This package groups the ECLYPSE builders inspired by the released
DeathStarBench applications. It currently includes hotel reservation,
social-network posting, and movie-review workflows modelled after the
original benchmark suite.

Source:
    `DeathStarBench repository
    <https://github.com/delimitrou/DeathStarBench>`_
"""

from .hotel_reservation.application import get_hotel_reservation
from .media_service.application import get_media_service
from .social_network.application import get_social_network

__all__ = [
    "get_hotel_reservation",
    "get_media_service",
    "get_social_network",
]
