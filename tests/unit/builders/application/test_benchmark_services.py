from __future__ import annotations

from types import SimpleNamespace

import pytest

from eclypse.builders.application.anomaly_detection import mpi_services as anomaly_mpi
from eclypse.builders.application.anomaly_detection import rest_services as anomaly_rest
from eclypse.builders.application.crud_api import mpi_services as crud_mpi
from eclypse.builders.application.crud_api import rest_services as crud_rest
from eclypse.builders.application.hotel_reservation import mpi_services as hotel_mpi
from eclypse.builders.application.hotel_reservation import rest_services as hotel_rest
from eclypse.builders.application.keyword_spotting import mpi_services as kws_mpi
from eclypse.builders.application.keyword_spotting import rest_services as kws_rest
from eclypse.builders.application.thumbnailer import mpi_services as thumb_mpi
from eclypse.builders.application.thumbnailer import rest_services as thumb_rest
from eclypse.builders.application.video_analytics_serving import (
    mpi_services as video_mpi,
)
from eclypse.builders.application.video_analytics_serving import (
    rest_services as video_rest,
)
from eclypse.remote.communication.rest.codes import HTTPStatusCode


class FakeRestResponse:
    def __init__(self, body):
        self.body = body
        self.data = body


class AwaitableResult:
    def __init__(self, result):
        self.result = result

    def __await__(self):
        async def _resolve():
            return self.result

        return _resolve().__await__()


class FakeRESTInterface:
    def __init__(self, handlers):
        self.handlers = handlers
        self.calls: list[tuple[str, str, dict[str, object]]] = []

    async def get(self, url: str, **kwargs):
        self.calls.append(("GET", url, kwargs))
        handler = self.handlers[("GET", url)]
        result = handler(**kwargs) if callable(handler) else handler
        return FakeRestResponse(result)

    async def post(self, url: str, **kwargs):
        self.calls.append(("POST", url, kwargs))
        handler = self.handlers[("POST", url)]
        result = handler(**kwargs) if callable(handler) else handler
        return FakeRestResponse(result)


class FakeMPIInterface:
    def __init__(self, messages):
        self.messages = list(messages)
        self.sent: list[tuple[str, dict[str, object]]] = []

    async def recv(self):
        return self.messages.pop(0)

    def send(self, recipient_id: str, body: dict[str, object]):
        self.sent.append((recipient_id, body))
        return AwaitableResult((recipient_id, body))


def _attach_service_logger(service):
    service.attach_node(
        SimpleNamespace(
            _logger=SimpleNamespace(
                bind=lambda **_: SimpleNamespace(info=lambda *_args: None)
            )
        )
    )
    return service


def test_rest_endpoints():
    detection_service = _attach_service_logger(
        video_rest.DetectionService("DetectionService")
    )
    search_service = _attach_service_logger(hotel_rest.SearchService("SearchService"))
    auth_service = _attach_service_logger(crud_rest.AuthService("AuthService"))
    preprocess_service = _attach_service_logger(
        kws_rest.PreprocessService("PreprocessService")
    )
    feature_service = _attach_service_logger(
        anomaly_rest.FeatureService("FeatureService")
    )
    thumbnail_service = _attach_service_logger(
        thumb_rest.TransformService("TransformService")
    )

    detect_code, detect_body = detection_service.detect(
        frame_id=1,
        stream_id="camera-a",
        objects=["person"],
    )
    search_code, search_body = search_service.search(city="Pisa", nights=2)
    auth_code, auth_body = auth_service.auth(api_key="demo")
    preprocess_code, preprocess_body = preprocess_service.preprocess(
        window_id=1,
        samples=[0.1, 0.2],
    )
    feature_code, feature_body = feature_service.features(
        window_id=1,
        samples=[0.8, 1.2, 4.5],
    )
    thumbnail_code, thumbnail_body = thumbnail_service.thumbnail(
        image_id="img-1",
        resolution=[1920, 1080],
    )

    assert detect_code == 200
    assert detect_body["detections"] == ["person"]
    assert search_code == 200
    assert search_body["hotels"][0]["id"] == "h1"
    assert auth_code == 200
    assert auth_body["status"] == "authorized"
    assert preprocess_code == 200
    assert preprocess_body["features"] == [1.0, 2.0]
    assert feature_code == 200
    assert feature_body["features"]["max"] == 4.5
    assert thumbnail_code == 200
    assert thumbnail_body["thumbnail"]["format"] == "jpeg"


@pytest.mark.asyncio
async def test_rest_workflows(monkeypatch):
    video_gateway = _attach_service_logger(
        video_rest.CameraGatewayService("CameraGatewayService")
    )
    video_gateway_rest = FakeRESTInterface(
        {
            ("POST", "DetectionService/detect"): {"detections": ["person"]},
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
    monkeypatch.setattr(
        type(video_gateway), "rest", property(lambda self: video_gateway_rest)
    )
    video_response = await video_gateway.step()
    assert video_response.body["object_count"] == 1

    hotel_frontend = _attach_service_logger(
        hotel_rest.FrontendService("FrontendService")
    )
    hotel_frontend_rest = FakeRESTInterface(
        {
            ("GET", "SearchService/search"): {
                "hotels": [{"id": "h1", "name": "Arno View", "price": 129.0}]
            },
            ("GET", "ProfileService/profile"): {
                "user": {"user_id": 101, "name": "Ada Lovelace"}
            },
            ("POST", "ReservationService/reserve"): {
                "reservation_id": "rsv-2001",
                "status": "confirmed",
            },
        }
    )
    monkeypatch.setattr(
        type(hotel_frontend), "rest", property(lambda self: hotel_frontend_rest)
    )
    hotel_response = await hotel_frontend.step()
    assert hotel_response.body["reservation_id"] == "rsv-2001"

    reservation_service = _attach_service_logger(
        hotel_rest.ReservationService("ReservationService")
    )
    reservation_rest = FakeRESTInterface(
        {
            ("POST", "PaymentService/pay"): {
                "transaction_id": "txn-1001",
                "status": "confirmed",
            }
        }
    )
    monkeypatch.setattr(
        type(reservation_service), "rest", property(lambda self: reservation_rest)
    )
    reservation_code, reservation_body = await reservation_service.reserve(
        hotel={"name": "Arno View", "price": 129.0},
        user={"name": "Ada Lovelace"},
    )
    assert reservation_code is HTTPStatusCode.CREATED
    assert reservation_body["transaction_id"] == "txn-1001"

    crud_gateway = _attach_service_logger(crud_rest.GatewayService("GatewayService"))
    crud_gateway_rest = FakeRESTInterface(
        {
            ("POST", "AuthService/auth"): {"token": "token:demo-key"},
            (
                "POST",
                "ItemService/items",
            ): {"status": "recorded", "items": [{"id": "item-1"}]},
        }
    )
    monkeypatch.setattr(
        type(crud_gateway), "rest", property(lambda self: crud_gateway_rest)
    )
    crud_response = await crud_gateway.step()
    assert crud_response.body["status"] == "recorded"

    item_service = _attach_service_logger(crud_rest.ItemService("ItemService"))
    item_rest = FakeRESTInterface(
        {
            ("POST", "AuditService/events"): {"status": "recorded"},
        }
    )
    monkeypatch.setattr(type(item_service), "rest", property(lambda self: item_rest))
    item_code, item_body = await item_service.create_item(
        token="token:demo",
        item={"id": "item-1", "name": "demo", "status": "active"},
    )
    assert item_code is HTTPStatusCode.CREATED
    assert item_body["items"][0]["id"] == "item-1"

    kws_sensor = _attach_service_logger(kws_rest.SensorService("SensorService"))
    kws_sensor_rest = FakeRESTInterface(
        {
            ("POST", "PreprocessService/preprocess"): {"features": [1.0, 3.0, 2.0]},
            ("POST", "InferenceService/infer"): {"keyword": "eclypse"},
            ("POST", "ActionService/action"): {"command": "wake"},
        }
    )
    monkeypatch.setattr(
        type(kws_sensor), "rest", property(lambda self: kws_sensor_rest)
    )
    kws_response = await kws_sensor.step()
    assert kws_response.body["command"] == "wake"

    anomaly_sensor = _attach_service_logger(anomaly_rest.SensorService("SensorService"))
    anomaly_sensor_rest = FakeRESTInterface(
        {
            (
                "POST",
                "FeatureService/features",
            ): {"features": {"max": 4.5, "mean": 2.1667}},
            ("POST", "InferenceService/score"): {"score": 2.08},
            ("POST", "AlertService/alert"): {"status": "normal", "score": 2.08},
        }
    )
    monkeypatch.setattr(
        type(anomaly_sensor), "rest", property(lambda self: anomaly_sensor_rest)
    )
    anomaly_response = await anomaly_sensor.step()
    assert anomaly_response.body["status"] == "normal"

    thumb_upload = _attach_service_logger(thumb_rest.UploadService("UploadService"))
    thumb_upload_rest = FakeRESTInterface(
        {
            (
                "POST",
                "TransformService/thumbnail",
            ): {"thumbnail": {"width": 320, "height": 180, "format": "jpeg"}},
            ("POST", "StorageService/store"): {"uri": "s3://thumbs/img-1.jpg"},
            ("POST", "NotificationService/notify"): {"status": "stored"},
        }
    )
    monkeypatch.setattr(
        type(thumb_upload), "rest", property(lambda self: thumb_upload_rest)
    )
    thumb_response = await thumb_upload.step()
    assert thumb_response.body["status"] == "stored"


@pytest.mark.asyncio
async def test_mpi_workflows(monkeypatch):
    video_gateway = _attach_service_logger(
        video_mpi.CameraGatewayService("CameraGatewayService")
    )
    video_mpi_interface = FakeMPIInterface(
        [{"response_type": "analytics_result", "object_count": 1, "summary": "person"}]
    )
    monkeypatch.setattr(
        type(video_gateway), "mpi", property(lambda self: video_mpi_interface)
    )
    video_response = await video_gateway.step()
    assert video_mpi_interface.sent[0][0] == "DetectionService"
    assert video_response["object_count"] == 1

    hotel_frontend = _attach_service_logger(
        hotel_mpi.FrontendService("FrontendService")
    )
    hotel_frontend_mpi = FakeMPIInterface(
        [
            {"hotels": [{"id": "h1", "name": "Arno View", "price": 129.0}]},
            {"user": {"user_id": 101, "name": "Ada Lovelace"}},
            {"reservation_id": "rsv-2001", "status": "confirmed"},
        ]
    )
    monkeypatch.setattr(
        type(hotel_frontend), "mpi", property(lambda self: hotel_frontend_mpi)
    )
    hotel_response = await hotel_frontend.step()
    assert hotel_frontend_mpi.sent[2][0] == "ReservationService"
    assert hotel_response["reservation_id"] == "rsv-2001"

    reservation_service = _attach_service_logger(
        hotel_mpi.ReservationService("ReservationService")
    )
    reservation_mpi = FakeMPIInterface(
        [
            {
                "sender_id": "FrontendService",
                "request_type": "create_reservation",
                "hotel": {"name": "Arno View", "price": 129.0},
                "user": {"name": "Ada Lovelace"},
            },
            {
                "sender_id": "PaymentService",
                "transaction_id": "txn-1001",
                "status": "confirmed",
            },
        ]
    )
    monkeypatch.setattr(
        type(reservation_service), "mpi", property(lambda self: reservation_mpi)
    )
    await reservation_service.step()
    assert reservation_mpi.sent[0][0] == "PaymentService"
    assert reservation_mpi.sent[1][0] == "FrontendService"

    crud_gateway = _attach_service_logger(crud_mpi.GatewayService("GatewayService"))
    crud_gateway_mpi = FakeMPIInterface(
        [
            {"token": "token:demo-key"},
            {"status": "recorded", "items": [{"id": "item-1"}]},
        ]
    )
    monkeypatch.setattr(
        type(crud_gateway), "mpi", property(lambda self: crud_gateway_mpi)
    )
    crud_response = await crud_gateway.step()
    assert crud_gateway_mpi.sent[1][0] == "ItemService"
    assert crud_response["status"] == "recorded"

    item_service = _attach_service_logger(crud_mpi.ItemService("ItemService"))
    item_mpi = FakeMPIInterface(
        [
            {
                "sender_id": "GatewayService",
                "request_type": "create_item",
                "token": "token:demo",
                "item": {"id": "item-1", "name": "demo", "status": "active"},
            },
            {"sender_id": "AuditService", "status": "recorded"},
        ]
    )
    monkeypatch.setattr(type(item_service), "mpi", property(lambda self: item_mpi))
    await item_service.step()
    assert item_mpi.sent[0][0] == "AuditService"
    assert item_mpi.sent[1][1]["items"][0]["id"] == "item-1"

    kws_sensor = _attach_service_logger(kws_mpi.SensorService("SensorService"))
    kws_sensor_mpi = FakeMPIInterface([{"command": "wake"}])
    monkeypatch.setattr(type(kws_sensor), "mpi", property(lambda self: kws_sensor_mpi))
    kws_response = await kws_sensor.step()
    assert kws_sensor_mpi.sent[0][0] == "PreprocessService"
    assert kws_response["command"] == "wake"

    anomaly_sensor = _attach_service_logger(anomaly_mpi.SensorService("SensorService"))
    anomaly_sensor_mpi = FakeMPIInterface([{"status": "alert", "score": 2.7}])
    monkeypatch.setattr(
        type(anomaly_sensor), "mpi", property(lambda self: anomaly_sensor_mpi)
    )
    anomaly_response = await anomaly_sensor.step()
    assert anomaly_sensor_mpi.sent[0][0] == "FeatureService"
    assert anomaly_response["status"] == "alert"

    thumb_upload = _attach_service_logger(thumb_mpi.UploadService("UploadService"))
    thumb_upload_mpi = FakeMPIInterface(
        [{"status": "stored", "uri": "s3://thumbs/img-1.jpg"}]
    )
    monkeypatch.setattr(
        type(thumb_upload), "mpi", property(lambda self: thumb_upload_mpi)
    )
    thumb_response = await thumb_upload.step()
    assert thumb_upload_mpi.sent[0][0] == "TransformService"
    assert thumb_response["status"] == "stored"
