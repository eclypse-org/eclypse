from __future__ import annotations

import pytest

from eclypse.builders.application.video_analytics_serving import (
    mpi_services as video_mpi,
)
from eclypse.builders.application.video_analytics_serving import (
    rest_services as video_rest,
)
from tests.unit.builders.application._service_test_helpers import (
    FakeRESTInterface,
    attach_service_logger,
    set_mpi,
)


@pytest.mark.asyncio
async def test_video_analytics_services(monkeypatch):
    assert video_rest.AnalyticsService is not None
    assert video_mpi.AnalyticsService is not None

    detection = attach_service_logger(video_rest.DetectionService("DetectionService"))
    tracking = attach_service_logger(video_rest.TrackingService("TrackingService"))
    analytics = attach_service_logger(video_rest.AnalyticsService("AnalyticsService"))
    gateway = attach_service_logger(
        video_rest.CameraGatewayService("CameraGatewayService")
    )

    code, body = detection.detect(1, "camera-a", ["person", "forklift"])
    assert code == 200
    assert body["detections"] == ["person", "forklift"]

    code, body = tracking.track(1, "camera-a", ["person", "forklift"])
    assert code == 200
    assert body["tracks"][1]["track_id"] == 2

    code, body = analytics.analyse(
        1,
        "camera-a",
        [{"label": "person", "track_id": 1}, {"label": "forklift", "track_id": 2}],
    )
    assert code == 200
    assert body["summary"] == "person, forklift"

    gateway_rest = FakeRESTInterface(
        {
            ("POST", "DetectionService/detect"): {"detections": ["person", "forklift"]},
            (
                "POST",
                "TrackingService/track",
            ): {"tracks": [{"label": "person", "track_id": 1}]},
            (
                "POST",
                "AnalyticsService/analyse",
            ): {"summary": "person", "object_count": 1},
        }
    )
    monkeypatch.setattr(type(gateway), "rest", property(lambda self: gateway_rest))
    response = await gateway.step()
    assert response.body["object_count"] == 1
    assert gateway_rest.calls[-1][1] == "AnalyticsService/analyse"

    mpi_detection = attach_service_logger(
        video_mpi.DetectionService("DetectionService")
    )
    mpi_tracking = attach_service_logger(video_mpi.TrackingService("TrackingService"))
    mpi_analytics = attach_service_logger(
        video_mpi.AnalyticsService("AnalyticsService")
    )
    mpi_gateway = attach_service_logger(
        video_mpi.CameraGatewayService("CameraGatewayService")
    )

    detection_comm = set_mpi(
        mpi_detection,
        [
            {
                "sender_id": "CameraGatewayService",
                "request_type": "analyse_frame",
                "frame_id": 1,
                "stream_id": "camera-a",
                "objects": ["person", "forklift"],
            }
        ],
    )
    await mpi_detection.step()
    assert detection_comm.sent == [
        (
            "TrackingService",
            {
                "request_type": "track_objects",
                "frame_id": 1,
                "stream_id": "camera-a",
                "detections": ["person", "forklift"],
            },
        )
    ]

    tracking_comm = set_mpi(
        mpi_tracking,
        [
            {
                "sender_id": "DetectionService",
                "request_type": "track_objects",
                "frame_id": 1,
                "stream_id": "camera-a",
                "detections": ["person"],
            }
        ],
    )
    await mpi_tracking.step()
    assert tracking_comm.sent[0][0] == "AnalyticsService"
    assert tracking_comm.sent[0][1]["tracks"][0]["label"] == "person"

    analytics_comm = set_mpi(
        mpi_analytics,
        [
            {
                "sender_id": "TrackingService",
                "request_type": "aggregate_events",
                "frame_id": 1,
                "stream_id": "camera-a",
                "tracks": [{"label": "person", "track_id": 1}],
            }
        ],
    )
    await mpi_analytics.step()
    assert analytics_comm.sent == [
        (
            "CameraGatewayService",
            {
                "response_type": "analytics_result",
                "frame_id": 1,
                "stream_id": "camera-a",
                "object_count": 1,
                "summary": "person",
            },
        )
    ]

    gateway_comm = set_mpi(
        mpi_gateway,
        [{"response_type": "analytics_result", "object_count": 1, "summary": "person"}],
    )
    gateway_response = await mpi_gateway.step()
    assert gateway_comm.sent[0][0] == "DetectionService"
    assert gateway_response["summary"] == "person"
