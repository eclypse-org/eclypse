from __future__ import annotations

from eclypse.builders import application as application_builders
from eclypse.builders import infrastructure as infrastructure_builders


def test_builder_exports_are_available():
    assert callable(application_builders.get_anomaly_detection)
    assert callable(application_builders.get_crud_api)
    assert callable(application_builders.get_hotel_reservation)
    assert callable(application_builders.get_keyword_spotting)
    assert callable(application_builders.get_sock_shop)
    assert callable(application_builders.get_thumbnailer)
    assert callable(application_builders.get_video_analytics_serving)
    assert callable(infrastructure_builders.get_orion_cev)
