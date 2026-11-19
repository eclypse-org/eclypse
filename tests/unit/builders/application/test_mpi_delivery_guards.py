from __future__ import annotations

from importlib import import_module
from types import SimpleNamespace

import pytest

from eclypse.builders.application.crud_api.mpi_services import GatewayService
from eclypse.remote.communication.mpi import Response
from eclypse.remote.utils import ResponseCode
from tests.unit.builders.application._service_test_helpers import (
    AwaitableResult,
    attach_service_logger,
    set_mpi,
)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("module", "service_name", "send_method"),
    [
        ("anomaly_detection", "SensorService", "capture_window"),
        ("keyword_spotting", "SensorService", "capture_window"),
        ("thumbnailer", "UploadService", "upload_image"),
        ("video_analytics_serving", "CameraGatewayService", "start_pipeline"),
        ("crud_api", "GatewayService", "auth_request"),
        ("crud_api", "ItemService", "gateway_request"),
        ("sock_shop", "FrontendService", "catalog_request"),
        ("sock_shop", "OrderService", "frontend_request"),
        ("deathstarbench.hotel_reservation", "FrontendService", "search_request"),
        ("deathstarbench.hotel_reservation", "ReservationService", "frontend_request"),
        ("deathstarbench.media_service", "ComposeReviewService", "submit_review"),
        ("deathstarbench.media_service", "MovieInfoService", "request_cast"),
        ("deathstarbench.social_network", "ComposePostService", "submit_post"),
        ("deathstarbench.social_network", "HomeTimelineService", "handle_request"),
    ],
)
@pytest.mark.parametrize(
    "code",
    [
        ResponseCode.NOT_CONNECTED,
        ResponseCode.ROUTE_NOT_FOUND,
        ResponseCode.RECIPIENT_UNAVAILABLE,
    ],
)
async def test_workflows_end_step_after_failed_delivery(
    monkeypatch, module, service_name, send_method, code
):
    services = import_module(f"eclypse.builders.application.{module}.mpi_services")
    service = attach_service_logger(getattr(services, service_name)(service_name))
    comm = set_mpi(service, [])

    async def fail_delivery(*_args):
        return SimpleNamespace(
            response=Response(code, message="Delivery failed."), ok=False
        )

    monkeypatch.setattr(service, send_method, fail_delivery)
    # An attempted recv would exhaust the empty fake queue and fail this test.
    assert await service.step() is None
    assert comm.sent == []


@pytest.mark.asyncio
async def test_gateway_checks_second_delivery_before_receiving(monkeypatch):
    service = attach_service_logger(GatewayService("GatewayService"))
    comm = set_mpi(service, [{"token": "demo-token"}])
    calls = []

    def send(recipient, data):
        calls.append((recipient, data))
        code = ResponseCode.OK if len(calls) == 1 else ResponseCode.ROUTE_NOT_FOUND
        return AwaitableResult(
            SimpleNamespace(response=Response(code), ok=code == ResponseCode.OK)
        )

    monkeypatch.setattr(comm, "send", send)
    assert await service.step() is None
    assert [recipient for recipient, _ in calls] == ["AuthService", "ItemService"]
