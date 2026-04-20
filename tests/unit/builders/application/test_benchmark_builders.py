from __future__ import annotations

import pytest

from eclypse.builders.application import (
    get_anomaly_detection,
    get_crud_api,
    get_hotel_reservation,
    get_keyword_spotting,
    get_thumbnailer,
    get_video_analytics_serving,
)
from eclypse.remote.service.service import Service


@pytest.mark.parametrize(
    ("builder", "expected_edge", "expected_flow_count"),
    [
        (
            get_video_analytics_serving,
            ("CameraGatewayService", "DetectionService"),
            2,
        ),
        (get_hotel_reservation, ("FrontendService", "SearchService"), 3),
        (get_crud_api, ("GatewayService", "AuthService"), 2),
        (get_keyword_spotting, ("SensorService", "PreprocessService"), 1),
        (get_anomaly_detection, ("SensorService", "FeatureService"), 1),
        (get_thumbnailer, ("UploadService", "TransformService"), 1),
    ],
)
def test_benchmark_builders(builder, expected_edge, expected_flow_count):
    plain_app = builder(include_default_assets=True)
    mpi_app = builder(include_default_assets=True, communication_interface="mpi")
    rest_app = builder(include_default_assets=True, communication_interface="rest")

    assert plain_app.has_logic is False
    assert mpi_app.has_logic is True
    assert rest_app.has_logic is True
    assert all(isinstance(service, Service) for service in mpi_app.services.values())
    assert all(isinstance(service, Service) for service in rest_app.services.values())
    assert plain_app.has_edge(*expected_edge)
    assert len(plain_app.flows) == expected_flow_count


@pytest.mark.parametrize(
    "builder",
    [
        get_video_analytics_serving,
        get_hotel_reservation,
        get_crud_api,
        get_keyword_spotting,
        get_anomaly_detection,
        get_thumbnailer,
    ],
)
def test_reject_unknown_interfaces(builder):
    with pytest.raises(ValueError, match="Unknown communication interface"):
        builder(communication_interface="grpc")  # type: ignore[arg-type]
