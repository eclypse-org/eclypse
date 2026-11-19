from __future__ import annotations

import asyncio
from concurrent.futures import Future
from datetime import datetime
from types import SimpleNamespace

import pytest

from eclypse.remote.communication.mpi import (
    EclypseMPI,
    Response,
)
from eclypse.remote.communication.request import (
    RouteNotFoundError,
    _process_request,
)
from eclypse.remote.communication.rest import EclypseREST
from eclypse.remote.communication.route import Route
from eclypse.remote.node.node import RemoteNode
from eclypse.remote.utils import ResponseCode


def route_future(*, remote=False):
    future = asyncio.get_running_loop().create_future()
    future.set_result(
        Route("sender", "node-a", "worker", "node-b" if remote else "node-a", 0)
    )
    return future


def test_response_preserves_positional_arguments_and_diagnostics():
    timestamp = datetime(2026, 1, 1)
    response = Response(
        ResponseCode.ROUTE_NOT_FOUND, timestamp, message="No route to worker."
    )
    assert response.timestamp is timestamp
    assert str(response) == repr(response)
    assert "ROUTE_NOT_FOUND: No route to worker." in str(response)
    assert Response().message is None
    assert ResponseCode.OK.value == 1
    assert ResponseCode.ERROR.value == 2


@pytest.mark.asyncio
@pytest.mark.parametrize("recipients", ["missing", ["online", "missing", "offline"]])
async def test_missing_mpi_routes_complete_with_ordered_outcomes(
    monkeypatch, recipients
):
    loop = asyncio.get_running_loop()
    completed = []

    async def entrypoint(route, _interface, **_data):
        await asyncio.sleep(0)
        completed.append(route.recipient_id)
        return Response(
            ResponseCode.NOT_CONNECTED
            if route.recipient_id == "offline"
            else ResponseCode.OK
        )

    service = SimpleNamespace(
        id="sender",
        node=SimpleNamespace(engine_loop=loop, service_comm_entrypoint=entrypoint),
    )
    mpi = EclypseMPI(service)

    def request_route(recipient):
        future = Future()
        future.set_result(
            None
            if recipient == "missing"
            else Route("sender", "node-a", recipient, "node-a", 0)
        )
        return SimpleNamespace(future=lambda: future)

    monkeypatch.setattr(mpi, "request_route", request_route)
    monkeypatch.setattr(
        "eclypse.remote.communication.request.ray_backend.get_size", lambda _: 0
    )
    request = await mpi.send(recipients, {})

    expected = (
        [ResponseCode.ROUTE_NOT_FOUND]
        if isinstance(recipients, str)
        else [ResponseCode.OK, ResponseCode.ROUTE_NOT_FOUND, ResponseCode.NOT_CONNECTED]
    )
    assert [response.code for response in request.responses] == expected
    assert all(elapsed.total_seconds() >= 0 for elapsed in request.elapsed_times)
    if isinstance(recipients, str):
        assert request.route is None
        assert "missing" in request.response.message
    else:
        assert request.routes[1] is None
        assert set(completed) == {"online", "offline"}


@pytest.mark.asyncio
async def test_rest_missing_route_still_raises():
    route = asyncio.get_running_loop().create_future()
    route.set_result(None)
    with pytest.raises(RouteNotFoundError, match="Route to worker not found"):
        await _process_request({}, 0, route, "worker", EclypseREST(SimpleNamespace()))


@pytest.mark.asyncio
async def test_missing_service_returns_mpi_failure_but_preserves_rest_error():
    node = object.__new__(RemoteNode)
    node._services = {}
    node._node_id = "node-a"
    route = route_future().result()
    response = await node.service_comm_entrypoint(route, EclypseMPI)
    assert response.code is ResponseCode.RECIPIENT_UNAVAILABLE
    assert "worker" in response.message
    with pytest.raises(KeyError, match="worker"):
        await node.service_comm_entrypoint(route, EclypseREST)


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "failure", ["lookup", "died", "unavailable", "bug", "cancelled"]
)
async def test_remote_delivery_translates_only_recognised_failures(failure):
    exceptions = pytest.importorskip("ray.exceptions")
    error = {
        "lookup": ValueError("Actor not found"),
        "died": exceptions.ActorDiedError(),
        "unavailable": exceptions.ActorUnavailableError("connection lost", None),
        "bug": ValueError("application bug"),
        "cancelled": asyncio.CancelledError(),
    }[failure]

    async def deliver(*_args, **_kwargs):
        raise error

    def get_actor(_name):
        if failure == "lookup":
            raise error
        return SimpleNamespace(service_comm_entrypoint=SimpleNamespace(remote=deliver))

    service = SimpleNamespace(
        infrastructure_id="infra", node=SimpleNamespace(get_actor=get_actor)
    )
    mpi = EclypseMPI(service)
    if failure in {"bug", "cancelled"}:
        with pytest.raises(type(error)) as caught:
            await _process_request({}, 0, route_future(remote=True), "worker", mpi)
        assert caught.value is error
    else:
        response = await _process_request(
            {}, 0, route_future(remote=True), "worker", mpi
        )
        assert response["future"].code is ResponseCode.RECIPIENT_UNAVAILABLE
        assert "worker" in response["future"].message
        # REST keeps the original exception rather than receiving an MPI object.
        with pytest.raises(type(error)) as caught:
            await _process_request(
                {}, 0, route_future(remote=True), "worker", EclypseREST(service)
            )
        assert caught.value is error


@pytest.mark.asyncio
async def test_local_programming_error_is_not_converted():
    async def deliver(*_args, **_kwargs):
        raise KeyError("application bug")

    mpi = EclypseMPI(
        SimpleNamespace(node=SimpleNamespace(service_comm_entrypoint=deliver))
    )
    with pytest.raises(KeyError, match="application bug"):
        await _process_request({}, 0, route_future(), "worker", mpi)
