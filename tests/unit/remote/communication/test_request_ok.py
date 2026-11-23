from __future__ import annotations

import asyncio

import pytest

from eclypse.remote.communication.mpi import Response
from eclypse.remote.communication.mpi.requests import (
    MulticastRequest,
    UnicastRequest,
)
from eclypse.remote.communication.rest.http_request import HTTPRequest
from eclypse.remote.utils import ResponseCode


@pytest.mark.asyncio
@pytest.mark.parametrize("code", list(ResponseCode))
async def test_mpi_ok_uses_delivery_outcomes(code):
    request = object.__new__(MulticastRequest)
    future = asyncio.get_running_loop().create_future()
    future.set_result({"future": Response(code)})
    request._futures = [future]
    assert request.ok is (code == ResponseCode.OK)


@pytest.mark.asyncio
async def test_multicast_ok_checks_all_recipients_and_requires_completion():
    request = object.__new__(MulticastRequest)
    loop = asyncio.get_running_loop()
    failed = loop.create_future()
    failed.set_result({"future": Response(ResponseCode.ROUTE_NOT_FOUND)})
    pending = loop.create_future()
    request._futures = [failed, pending]
    with pytest.raises(RuntimeError, match="Request not completed yet"):
        _ = request.ok
    pending.set_result({"future": Response()})
    assert request.ok is False
    request._futures = [pending, pending]
    assert request.ok is True
    request._futures = []
    assert request.ok is True


@pytest.mark.asyncio
@pytest.mark.parametrize("status", [199, 200, 201, 204, 299, 300])
async def test_rest_ok_accepts_only_2xx(status):
    request = object.__new__(HTTPRequest)
    future = asyncio.get_running_loop().create_future()
    future.set_result({"future": (status, {})})
    request._futures = [future]
    assert request.ok is (200 <= status < 300)


@pytest.mark.asyncio
@pytest.mark.parametrize("request_type", [UnicastRequest, HTTPRequest])
async def test_ok_before_completion_raises_then_reports_success(request_type):
    request = object.__new__(request_type)
    future = asyncio.get_running_loop().create_future()
    request._futures = [future]
    with pytest.raises(RuntimeError, match="Request not completed yet"):
        _ = request.ok
    response = (200, {}) if request_type is HTTPRequest else Response()
    future.set_result({"future": response})
    assert request.ok is True


@pytest.mark.asyncio
@pytest.mark.parametrize("request_type", [UnicastRequest, HTTPRequest])
@pytest.mark.parametrize("cancelled", [True, False])
async def test_ok_propagates_future_errors_and_cancellation(request_type, cancelled):
    request = object.__new__(request_type)
    future = asyncio.get_running_loop().create_future()
    request._futures = [future]
    if cancelled:
        future.cancel()
        with pytest.raises(asyncio.CancelledError):
            _ = request.ok
    else:
        future.set_exception(ValueError("delivery bug"))
        with pytest.raises(ValueError, match="delivery bug"):
            _ = request.ok
