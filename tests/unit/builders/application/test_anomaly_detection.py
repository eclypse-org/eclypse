from __future__ import annotations

import pytest

from eclypse.builders.application import get_anomaly_detection
from eclypse.remote.service.service import Service


def test_anomaly_detection_builder():
    plain_app = get_anomaly_detection(include_default_assets=True)
    mpi_app = get_anomaly_detection(
        include_default_assets=True,
        communication_interface="mpi",
    )
    rest_app = get_anomaly_detection(
        include_default_assets=True,
        communication_interface="rest",
    )

    assert plain_app.has_logic is False
    assert mpi_app.has_logic is True
    assert rest_app.has_logic is True
    assert all(isinstance(service, Service) for service in mpi_app.services.values())
    assert all(isinstance(service, Service) for service in rest_app.services.values())
    assert plain_app.has_edge("SensorService", "FeatureService")
    assert len(plain_app.flows) == 1


def test_anomaly_detection_rejects_unknown_interfaces():
    with pytest.raises(ValueError, match="Unknown communication interface"):
        get_anomaly_detection(communication_interface="grpc")  # type: ignore[arg-type]
