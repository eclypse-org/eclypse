"""Application builders."""

from .anomaly_detection.application import get_anomaly_detection
from .crud_api.application import get_crud_api
from .deathstarbench.hotel_reservation.application import get_hotel_reservation
from .deathstarbench.media_service.application import get_media_service
from .deathstarbench.social_network.application import get_social_network
from .keyword_spotting.application import get_keyword_spotting
from .sock_shop.application import get_sock_shop
from .thumbnailer.application import get_thumbnailer
from .video_analytics_serving.application import get_video_analytics_serving

__all__ = [
    "get_anomaly_detection",
    "get_crud_api",
    "get_hotel_reservation",
    "get_keyword_spotting",
    "get_media_service",
    "get_social_network",
    "get_sock_shop",
    "get_thumbnailer",
    "get_video_analytics_serving",
]
