from __future__ import annotations

from eclypse.builders import application as application_builders
from eclypse.builders import infrastructure as infrastructure_builders
from eclypse.builders import workflow as workflow_builders


def test_builder_exports_are_available():
    assert callable(application_builders.get_anomaly_detection)
    assert callable(application_builders.get_crud_api)
    assert callable(application_builders.get_hotel_reservation)
    assert callable(application_builders.get_keyword_spotting)
    assert callable(application_builders.get_media_service)
    assert callable(application_builders.get_sock_shop)
    assert callable(application_builders.get_social_network)
    assert callable(application_builders.get_thumbnailer)
    assert callable(application_builders.get_video_analytics_serving)
    assert callable(infrastructure_builders.get_continuum_tiered)
    assert callable(infrastructure_builders.get_factory_cells)
    assert callable(infrastructure_builders.get_backbone)
    assert callable(infrastructure_builders.get_caida)
    assert callable(infrastructure_builders.get_gabriel)
    assert callable(infrastructure_builders.get_orion_cev)
    assert callable(infrastructure_builders.get_sndlib)
    assert callable(infrastructure_builders.get_topohub)
    assert callable(infrastructure_builders.get_topology_zoo)
    assert callable(infrastructure_builders.get_industrial_tsn)
    assert callable(infrastructure_builders.get_mec_5g)
    assert callable(infrastructure_builders.get_multi_region_wan)
    assert callable(infrastructure_builders.get_scale_free)
    assert callable(infrastructure_builders.get_small_world)
    assert callable(infrastructure_builders.get_vehicular_edge)
    assert callable(workflow_builders.get_workflow)
