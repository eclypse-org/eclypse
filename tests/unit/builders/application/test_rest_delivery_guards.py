from __future__ import annotations

from importlib import import_module
from types import SimpleNamespace

import pytest

from eclypse.builders.application.crud_api.rest_services import (
    GatewayService,
    ItemService,
)
from eclypse.builders.application.deathstarbench.hotel_reservation import (
    rest_services as hotel_rest,
)
from eclypse.builders.application.deathstarbench.media_service.rest_services import (
    MovieInfoService,
)
from tests.unit.builders.application._service_test_helpers import (
    FakeRestResponse,
    attach_service_logger,
)


@pytest.mark.asyncio
@pytest.mark.parametrize("failed_call", [1, 2])
async def test_rest_gateway_stops_before_reading_failed_response(failed_call):
    service = attach_service_logger(GatewayService("gateway"))
    calls = []

    async def post(url, **_data):
        calls.append(url)
        if len(calls) == failed_call:
            return FakeRestResponse(
                {"error": "route_not_found", "message": "No route."}, 503
            )
        return FakeRestResponse({"token": "demo-token"}, 201)

    service._comm = SimpleNamespace(post=post)
    assert await service.step() is None
    assert len(calls) == failed_call


@pytest.mark.asyncio
@pytest.mark.parametrize("failed_call", [1, 2, 3])
@pytest.mark.parametrize("status", [404, 503])
async def test_rest_aggregator_propagates_downstream_error_unchanged(
    failed_call, status
):
    service = attach_service_logger(MovieInfoService("movie-info"))
    calls = []
    error = {"error": "recipient_unavailable", "message": "Worker unavailable."}

    async def get(url, **_data):
        calls.append(url)
        if len(calls) == failed_call:
            return FakeRestResponse(error, status)
        return FakeRestResponse({}, 204)

    service._comm = SimpleNamespace(get=get)
    code, body = await service.details("movie-1", "Demo")
    assert code == status
    assert body is error
    assert len(calls) == failed_call


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("service_type", "method", "data"),
    [
        (ItemService, "create_item", {"token": "demo", "item": {"id": "item-1"}}),
        (
            hotel_rest.ReservationService,
            "reserve",
            {"hotel": {"price": 50}, "user": {}},
        ),
    ],
)
async def test_rest_endpoint_preserves_failure_status_and_diagnostics(
    service_type, method, data
):
    service = attach_service_logger(service_type("service"))
    error = {"error": "not_connected", "message": "Recipient disconnected."}

    async def post(_url, **_data):
        return FakeRestResponse(error, 503)

    service._comm = SimpleNamespace(post=post)
    code, body = await getattr(service, method)(**data)
    assert code == 503
    assert body is error


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("module", "service_name", "replies", "failed_call"),
    [
        (module, name, replies, failed_call)
        for module, name, replies in [
            (
                "anomaly_detection",
                "SensorService",
                [{"features": [1]}, {"score": 0.9}, {}],
            ),
            (
                "keyword_spotting",
                "SensorService",
                [{"features": [1]}, {"keyword": "stop"}, {}],
            ),
            ("thumbnailer", "UploadService", [{"thumbnail": {}}, {"uri": "img-1"}, {}]),
            (
                "video_analytics_serving",
                "CameraGatewayService",
                [{"detections": []}, {"tracks": []}, {}],
            ),
            (
                "deathstarbench.hotel_reservation",
                "FrontendService",
                [{"hotels": [{}]}, {"user": {}}, {}],
            ),
            ("sock_shop", "FrontendService", [{"products": []}, {}, {"items": []}, {}]),
            ("deathstarbench.media_service", "ComposeReviewService", [{}]),
            ("deathstarbench.social_network", "ComposePostService", [{}]),
        ]
        for failed_call in range(1, len(replies) + 1)
    ],
)
async def test_rest_workflow_stops_at_each_failed_stage(
    module, service_name, replies, failed_call
):
    services = import_module(f"eclypse.builders.application.{module}.rest_services")
    service = attach_service_logger(getattr(services, service_name)(service_name))
    calls = []
    error = {"error": "recipient_unavailable", "message": "Stage unavailable."}

    async def request(url, **data):
        calls.append((url, data))
        if len(calls) == failed_call:
            return FakeRestResponse(error, 503)
        return FakeRestResponse(replies[len(calls) - 1])

    service._comm = SimpleNamespace(get=request, post=request)
    assert await service.step() is None
    assert len(calls) == failed_call


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ("module", "service_name", "method", "data"),
    [
        ("media_service", "UniqueIdService", "compose", {}),
        ("media_service", "MovieIdService", "compose", {"movie_title": "The Matrix"}),
        ("media_service", "TextService", "compose", {"text": "Review"}),
        ("media_service", "RatingService", "compose", {"rating": 5}),
        (
            "media_service",
            "UserService",
            "compose",
            {"user_id": 101, "username": "alice"},
        ),
        (
            "media_service",
            "ReviewStorageService",
            "store",
            {
                "review_id": 1,
                "movie_id": "m1",
                "movie_title": "The Matrix",
                "rating": 5,
                "text": "Review",
                "user": {"user_id": 101},
                "reply_to": "frontend",
            },
        ),
        (
            "media_service",
            "UserReviewService",
            "write",
            {
                "review": {"review_id": 1, "user": {"user_id": 101}},
                "reply_to": "frontend",
            },
        ),
        ("social_network", "UniqueIdService", "compose", {}),
        ("social_network", "TextService", "compose", {"text": "Hello @bob"}),
        ("social_network", "UserMentionService", "compose", {"mentions": ["bob"]}),
        (
            "social_network",
            "UrlShortenService",
            "compose",
            {"urls": ["https://example.com"]},
        ),
        (
            "social_network",
            "MediaService",
            "compose",
            {"media_ids": [1], "media_types": ["image"]},
        ),
        (
            "social_network",
            "UserService",
            "compose",
            {"user_id": 101, "username": "alice"},
        ),
        (
            "social_network",
            "PostStorageService",
            "store",
            {
                "post_id": 1,
                "creator": {"user_id": 101},
                "text": "Hello",
                "user_mentions": [],
                "media": [],
                "shortened_urls": [],
                "reply_to": "frontend",
            },
        ),
        (
            "social_network",
            "UserTimelineService",
            "write",
            {
                "creator": {"user_id": 101},
                "post_id": 1,
                "post": {},
                "reply_to": "frontend",
            },
        ),
        ("social_network", "UserTimelineService", "read", {"user_id": 101}),
        (
            "social_network",
            "HomeTimelineService",
            "write",
            {
                "creator": {"user_id": 101},
                "post_id": 1,
                "reply_to": "frontend",
            },
        ),
        ("social_network", "HomeTimelineService", "read", {"user_id": 101}),
    ],
)
async def test_rest_forwarding_endpoints_preserve_downstream_failure(
    module, service_name, method, data
):
    services = import_module(
        f"eclypse.builders.application.deathstarbench.{module}.rest_services"
    )
    service = attach_service_logger(getattr(services, service_name)(service_name))
    calls = []
    error = {"error": "route_not_found", "message": "Downstream route unavailable."}

    async def request(url, **payload):
        calls.append((url, payload))
        return FakeRestResponse(error, 503)

    service._comm = SimpleNamespace(get=request, post=request)
    code, body = await getattr(service, method)(**data)
    assert code == 503
    assert body is error
    assert len(calls) == 1
