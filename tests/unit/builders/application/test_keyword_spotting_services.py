from __future__ import annotations

import pytest

from eclypse.builders.application.keyword_spotting import mpi_services as kws_mpi
from eclypse.builders.application.keyword_spotting import rest_services as kws_rest
from tests.unit.builders.application._service_test_helpers import (
    FakeRESTInterface,
    attach_service_logger,
    set_mpi,
)


@pytest.mark.asyncio
async def test_keyword_spotting_services(monkeypatch):
    preprocess = attach_service_logger(kws_rest.PreprocessService("PreprocessService"))
    inference = attach_service_logger(kws_rest.InferenceService("InferenceService"))
    action = attach_service_logger(kws_rest.ActionService("ActionService"))
    sensor = attach_service_logger(kws_rest.SensorService("SensorService"))

    code, body = preprocess.preprocess(1, [0.1, 0.3, 0.2])
    assert code == 200
    assert body["features"] == [1.0, 3.0, 2.0]

    code, body = inference.infer(1, [1.0, 3.0, 2.0])
    assert code == 200
    assert body["keyword"] == "eclypse"

    code, body = inference.infer(2, [1.0, 1.0])
    assert body["keyword"] == "background"

    code, body = action.action(1, "eclypse")
    assert code == 200
    assert body["command"] == "wake"

    code, body = action.action(2, "background")
    assert body["command"] == "idle"

    sensor_rest = FakeRESTInterface(
        {
            ("POST", "PreprocessService/preprocess"): {"features": [1.0, 3.0, 2.0]},
            ("POST", "InferenceService/infer"): {"keyword": "eclypse"},
            ("POST", "ActionService/action"): {"command": "wake"},
        }
    )
    monkeypatch.setattr(type(sensor), "rest", property(lambda self: sensor_rest))
    response = await sensor.step()
    assert response.body["command"] == "wake"

    mpi_preprocess = attach_service_logger(
        kws_mpi.PreprocessService("PreprocessService")
    )
    mpi_inference = attach_service_logger(kws_mpi.InferenceService("InferenceService"))
    mpi_action = attach_service_logger(kws_mpi.ActionService("ActionService"))
    mpi_sensor = attach_service_logger(kws_mpi.SensorService("SensorService"))

    preprocess_comm = set_mpi(
        mpi_preprocess,
        [
            {
                "sender_id": "SensorService",
                "request_type": "preprocess_audio",
                "window_id": 1,
                "samples": [0.1, 0.3, 0.2],
            }
        ],
    )
    await mpi_preprocess.step()
    assert preprocess_comm.sent[0][1]["features"] == [1.0, 3.0, 2.0]

    inference_comm = set_mpi(
        mpi_inference,
        [
            {
                "sender_id": "PreprocessService",
                "request_type": "run_inference",
                "window_id": 1,
                "features": [1.0, 3.0, 2.0],
            }
        ],
    )
    await mpi_inference.step()
    assert inference_comm.sent[0][1]["keyword"] == "eclypse"

    action_comm = set_mpi(
        mpi_action,
        [
            {
                "sender_id": "InferenceService",
                "request_type": "dispatch_action",
                "window_id": 1,
                "keyword": "background",
            }
        ],
    )
    await mpi_action.step()
    assert action_comm.sent[0][1]["command"] == "idle"

    sensor_comm = set_mpi(mpi_sensor, [{"command": "wake"}])
    response = await mpi_sensor.step()
    assert sensor_comm.sent[0][0] == "PreprocessService"
    assert response["command"] == "wake"
