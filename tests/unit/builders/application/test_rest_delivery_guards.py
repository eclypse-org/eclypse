from __future__ import annotations

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
