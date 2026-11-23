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


@pytest.mark.asyncio
@pytest.mark.parametrize(
    (
        "module",
        "service_name",
        "messages",
        "recipients",
        "initial_reads",
        "failed_call",
    ),
    [
        (module, name, messages, recipients, initial_reads, failed_call)
        for module, name, messages, recipients, initial_reads in [
            (
                "deathstarbench.hotel_reservation",
                "FrontendService",
                [{"hotels": [{}]}, {"user": {}}, {}],
                ["SearchService", "ProfileService", "ReservationService"],
                0,
            ),
            (
                "deathstarbench.media_service",
                "MovieInfoService",
                [
                    {"movie_id": "m1", "movie_title": "The Matrix"},
                    {"cast": []},
                    {"plot": "Demo"},
                    {"reviews": []},
                ],
                ["CastInfoService", "PlotService", "MovieReviewService"],
                1,
            ),
            (
                "sock_shop",
                "FrontendService",
                [{"products": []}, {}, {"items": []}, {}],
                ["CatalogService", "UserService", "CartService", "OrderService"],
                0,
            ),
            (
                "sock_shop",
                "OrderService",
                [{"items": []}, {"transaction_id": 1}, {"details": {}}],
                ["PaymentService", "ShippingService"],
                1,
            ),
        ]
        for failed_call in range(2, len(recipients) + 1)
    ],
)
async def test_mpi_workflow_does_not_receive_after_later_delivery_failure(
    monkeypatch, module, service_name, messages, recipients, initial_reads, failed_call
):
    services = import_module(f"eclypse.builders.application.{module}.mpi_services")
    service = attach_service_logger(getattr(services, service_name)(service_name))
    comm = set_mpi(service, messages)
    calls = []

    def send(recipient, data):
        calls.append((recipient, data))
        ok = len(calls) != failed_call
        code = ResponseCode.OK if ok else ResponseCode.RECIPIENT_UNAVAILABLE
        return AwaitableResult(SimpleNamespace(response=Response(code), ok=ok))

    monkeypatch.setattr(comm, "send", send)
    assert await service.step() is None
    assert [recipient for recipient, _ in calls] == recipients[:failed_call]
    consumed = initial_reads + failed_call - 1
    assert comm.messages == messages[consumed:]
