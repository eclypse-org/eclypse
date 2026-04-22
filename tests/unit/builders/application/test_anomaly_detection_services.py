from __future__ import annotations

import pytest

from eclypse.builders.application.anomaly_detection import mpi_services as anomaly_mpi
from eclypse.builders.application.anomaly_detection import rest_services as anomaly_rest
from tests.unit.builders.application._service_test_helpers import (
    FakeRESTInterface,
    attach_service_logger,
    set_mpi,
)


@pytest.mark.asyncio
async def test_anomaly_detection_services(monkeypatch):
    feature = attach_service_logger(anomaly_rest.FeatureService("FeatureService"))
    inference = attach_service_logger(anomaly_rest.InferenceService("InferenceService"))
    alert = attach_service_logger(anomaly_rest.AlertService("AlertService"))
    sensor = attach_service_logger(anomaly_rest.SensorService("SensorService"))

    code, body = feature.features(1, [0.8, 1.2, 4.5])
    assert code == 200
    assert body["features"]["max"] == 4.5

    code, body = inference.score(1, {"max": 4.5, "mean": 2.1667})
    assert code == 200
    assert body["score"] == pytest.approx(2.08)

    code, body = alert.alert(1, 2.08)
    assert code == 200
    assert body["status"] == "normal"

    code, body = alert.alert(2, 2.7)
    assert body["status"] == "alert"

    sensor_rest = FakeRESTInterface(
        {
            ("POST", "FeatureService/features"): {
                "features": {"max": 4.5, "mean": 2.1667}
            },
            ("POST", "InferenceService/score"): {"score": 2.08},
            ("POST", "AlertService/alert"): {"status": "normal", "score": 2.08},
        }
    )
    monkeypatch.setattr(type(sensor), "rest", property(lambda self: sensor_rest))
    response = await sensor.step()
    assert response.body["status"] == "normal"

    mpi_feature = attach_service_logger(anomaly_mpi.FeatureService("FeatureService"))
    mpi_inference = attach_service_logger(
        anomaly_mpi.InferenceService("InferenceService")
    )
    mpi_alert = attach_service_logger(anomaly_mpi.AlertService("AlertService"))
    mpi_sensor = attach_service_logger(anomaly_mpi.SensorService("SensorService"))

    feature_comm = set_mpi(
        mpi_feature,
        [
            {
                "sender_id": "SensorService",
                "request_type": "extract_features",
                "window_id": 1,
                "samples": [0.8, 1.2, 4.5],
            }
        ],
    )
    await mpi_feature.step()
    assert feature_comm.sent[0][1]["features"]["max"] == 4.5

    inference_comm = set_mpi(
        mpi_inference,
        [
            {
                "sender_id": "FeatureService",
                "request_type": "score_window",
                "window_id": 1,
                "features": {"max": 4.5, "mean": 2.1667},
            }
        ],
    )
    await mpi_inference.step()
    assert inference_comm.sent[0][1]["score"] == pytest.approx(2.08)

    alert_comm = set_mpi(
        mpi_alert,
        [
            {
                "sender_id": "InferenceService",
                "request_type": "emit_alert",
                "window_id": 1,
                "score": 2.7,
            }
        ],
    )
    await mpi_alert.step()
    assert alert_comm.sent[0][1]["status"] == "alert"

    sensor_comm = set_mpi(mpi_sensor, [{"status": "normal", "score": 2.08}])
    response = await mpi_sensor.step()
    assert sensor_comm.sent[0][0] == "FeatureService"
    assert response["status"] == "normal"
