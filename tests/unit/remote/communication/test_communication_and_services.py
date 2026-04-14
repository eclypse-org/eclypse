from __future__ import annotations

import asyncio
from concurrent.futures import Future
from datetime import datetime
from types import SimpleNamespace

import pytest

from eclypse.remote.communication.interface import EclypseCommunicationInterface
from eclypse.remote.communication.mpi.interface import (
    EclypseMPI,
    exchange,
)
from eclypse.remote.communication.mpi.response import Response
from eclypse.remote.communication.request import (
    EclypseRequest,
    RouteNotFoundError,
    _process_request,
)
from eclypse.remote.communication.rest.codes import HTTPStatusCode
from eclypse.remote.communication.rest.http_request import HTTPRequest
from eclypse.remote.communication.rest.interface import (
    EclypseREST,
    register_endpoint,
)
from eclypse.remote.communication.rest.methods import HTTPMethod
from eclypse.remote.communication.route import (
    Route,
    _get_bytes_size,
)
from eclypse.remote.service.rest import RESTService
from eclypse.remote.service.service import Service
from eclypse.remote.utils import ResponseCode


class ExampleObject:
    def __init__(self):
        self.payload = {"items": [1, 2, 3], "name": "demo"}


class DummyInterface(EclypseCommunicationInterface):
    async def _not_connected_response(self):
        return "offline"

    async def _execute_request(self, *args, **kwargs):
        return {"args": args, "kwargs": kwargs}


class DemoService(Service):
    async def step(self):
        return "step"


class DemoRESTHandlers:
    def __init__(self):
        self.id = "svc"
        self.application_id = "app"
        self.node = SimpleNamespace(manager_actor_name="edge-cloud/manager")
        self.event_loop = asyncio.new_event_loop()
        self._run_task = None

    @register_endpoint("/hello", "GET")
    def hello(self, name: str):
        return HTTPStatusCode.OK, {"name": name}

    @register_endpoint("/boom", "POST")
    def boom(self):
        raise RuntimeError("boom")

    @register_endpoint("/bad-data", "PUT")
    def bad_data(self):
        return HTTPStatusCode.OK, "bad"

    @register_endpoint("/bad-code", "DELETE")
    def bad_code(self):
        return 999, {}


class DuplicateRESTHandlers(DemoRESTHandlers):
    mpi = "skip"

    @register_endpoint("/dup", "GET")
    def first(self):
        return HTTPStatusCode.OK, {"handler": "first"}

    @register_endpoint("/dup", "GET")
    def second(self):
        return HTTPStatusCode.OK, {"handler": "second"}


class AsyncRESTHandlers(DemoRESTHandlers):
    mpi = "skip"

    @register_endpoint("/number", "GET")
    async def number(self):
        return 200, {"ok": True}


def test_route_response_and_http_request_helpers(monkeypatch):
    route = Route(
        sender_id="gateway",
        sender_node_id="edge-a",
        recipient_id="worker",
        recipient_node_id="edge-b",
        processing_time=25,
        hops=[("edge-a", "edge-b", {"latency": 5, "bandwidth": 100})],
    )
    response = Response(ResponseCode.OK)

    assert len(route) == 1
    assert route.no_hop is False
    assert route.network_cost > 0
    assert "Path from gateway" in str(route)
    assert str(response) == repr(response)

    def fake_init(self, recipient_ids, data, _comm, timestamp=None):
        self._recipient_ids = recipient_ids
        self._data = data
        self._timestamp = timestamp if timestamp is not None else datetime.now()
        self._routes = [SimpleNamespace(done=lambda: True, result=lambda: route)]
        self._futures = [
            SimpleNamespace(
                done=lambda: True,
                result=lambda: {
                    "future": (HTTPStatusCode.CREATED, {"ok": True}),
                    "timestamp": datetime.now(),
                },
            )
        ]

    monkeypatch.setattr(
        "eclypse.remote.communication.rest.http_request.EclypseRequest.__init__",
        fake_init,
    )

    request = HTTPRequest(
        "worker/resource", HTTPMethod.POST, {"value": 1}, SimpleNamespace()
    )

    assert request.recipient_ids == ["worker"]
    assert request.data["url"] == "worker/resource"
    assert request.route is route
    assert request.status_code is HTTPStatusCode.CREATED
    assert request.body == {"ok": True}

    pending_request = object.__new__(HTTPRequest)
    pending_request._routes = [SimpleNamespace(done=lambda: False)]
    pending_request._futures = [SimpleNamespace(done=lambda: False)]

    assert pending_request.route is None
    assert pending_request.response is None
    with pytest.raises(RuntimeError, match="Request not completed yet"):
        pending_request.status_code
    with pytest.raises(RuntimeError, match="Request not completed yet"):
        pending_request.body


def test_route_size_helper_handles_objects_and_nested_structures():
    obj = ExampleObject()

    assert _get_bytes_size({"nested": [1, 2, {"x": 3}]}) > 0
    assert _get_bytes_size(obj) == _get_bytes_size(obj.__dict__)


@pytest.mark.asyncio
async def test_request_initialisation_and_rest_request_wrappers(monkeypatch):
    loop = asyncio.get_running_loop()
    timestamp = datetime(2026, 1, 1, 0, 0, 0)
    route_futures: dict[str, Future[object]] = {}
    response_futures: list[Future[dict[str, object]]] = []

    for recipient_id in ("worker-a", "worker-b"):
        route_future: Future[object] = Future()
        route_future.set_result(SimpleNamespace(recipient_id=recipient_id))
        route_futures[recipient_id] = route_future

        response_future: Future[dict[str, object]] = Future()
        response_future.set_result(
            {
                "future": recipient_id,
                "timestamp": datetime(2026, 1, 1, 0, 0, 5),
            }
        )
        response_futures.append(response_future)

    monkeypatch.setattr(
        "eclypse.remote.communication.request.ray_backend.put",
        lambda value: f"ref:{value}",
    )

    def fake_run_coroutine_threadsafe(coro, loop=None):
        del loop
        coro.close()
        return response_futures.pop(0)

    monkeypatch.setattr(
        "eclypse.remote.communication.request.asyncio.run_coroutine_threadsafe",
        fake_run_coroutine_threadsafe,
    )

    comm = SimpleNamespace(
        service=SimpleNamespace(node=SimpleNamespace(engine_loop=loop)),
        request_route=lambda recipient_id: SimpleNamespace(
            future=lambda: route_futures[recipient_id]
        ),
    )
    request = EclypseRequest(
        ["worker-a", "worker-b"],
        {"payload": 3},
        comm,
        timestamp=timestamp,
    )

    assert request.data == {"payload": 3}
    assert request.timestamp is timestamp
    assert request.recipient_ids == ["worker-a", "worker-b"]
    assert len(request.routes) == 2
    assert await request is request
    assert request.responses == ["worker-a", "worker-b"]
    assert request.elapsed_times == [datetime(2026, 1, 1, 0, 0, 5) - timestamp] * 2
    assert request._ref_args == {"payload": "ref:3"}  # noqa: SLF001

    awaited_request = object.__new__(HTTPRequest)

    async def fake_request_await():
        return "awaited-request"

    monkeypatch.setattr(
        "eclypse.remote.communication.rest.http_request.EclypseRequest.__await__",
        lambda self: fake_request_await().__await__(),
    )

    assert await awaited_request == "awaited-request"


@pytest.mark.asyncio
async def test_process_request_and_base_interface_behaviour(monkeypatch):
    loop = asyncio.get_running_loop()
    route = Route(
        sender_id="gateway",
        sender_node_id="edge-a",
        recipient_id="worker",
        recipient_node_id="edge-b",
        processing_time=5,
        hops=[("edge-a", "edge-b", {"latency": 5, "bandwidth": 1000})],
    )
    route_future: asyncio.Future[Route | None] = loop.create_future()
    route_future.set_result(route)
    missing_route_future: asyncio.Future[Route | None] = loop.create_future()
    missing_route_future.set_result(None)

    sleep_calls: list[float] = []

    async def fake_sleep(delay: float):
        sleep_calls.append(delay)

    async def remote_entrypoint(_route, _comm_cls, **kwargs):
        return kwargs["payload"]

    monkeypatch.setattr(
        "eclypse.remote.communication.request.asyncio.sleep", fake_sleep
    )

    service = SimpleNamespace(
        infrastructure_id="edge-cloud",
        node=SimpleNamespace(
            get_actor=lambda actor_name: SimpleNamespace(
                service_comm_entrypoint=SimpleNamespace(remote=remote_entrypoint),
                actor_name=actor_name,
            ),
        ),
    )
    comm = SimpleNamespace(service=service)

    processed = await _process_request(
        {"payload": "value"},
        {"payload": "ref-value"},
        route_future,
        "worker",
        comm,
    )

    assert processed["future"] == "ref-value"
    assert sleep_calls

    same_node_route = Route(
        sender_id="gateway",
        sender_node_id="edge-a",
        recipient_id="gateway",
        recipient_node_id="edge-a",
        processing_time=0,
        hops=[],
    )
    same_node_future: asyncio.Future[Route | None] = loop.create_future()
    same_node_future.set_result(same_node_route)

    async def local_entrypoint(_route, _comm_cls, **kwargs):
        return kwargs["payload"]

    comm.service.node.service_comm_entrypoint = local_entrypoint

    same_node_result = await _process_request(
        {"payload": "direct"},
        {"payload": "unused"},
        same_node_future,
        "gateway",
        comm,
    )

    assert same_node_result["future"] == "direct"

    with pytest.raises(RouteNotFoundError, match="Route to worker not found"):
        await _process_request({}, {}, missing_route_future, "worker", comm)

    service_stub = SimpleNamespace(
        node=SimpleNamespace(manager_actor_name="edge-cloud/manager"),
        application_id="app",
        id="svc",
        event_loop="loop",
    )
    manager = SimpleNamespace(
        route=SimpleNamespace(
            remote=lambda app_id, service_id, recipient: (app_id, service_id, recipient)
        ),
        get_neighbors=SimpleNamespace(
            remote=lambda app_id, service_id: [app_id, service_id]
        ),
    )
    interface = DummyInterface(service_stub)

    with pytest.raises(ValueError, match="not connected"):
        interface.request_route("worker")

    monkeypatch.setattr(
        "eclypse.remote.communication.interface.ray_backend.get_actor",
        lambda name: manager if name == "edge-cloud/manager" else None,
    )
    monkeypatch.setattr(
        "eclypse.remote.communication.interface.asyncio.wrap_future",
        lambda future: future,
    )

    def fake_schedule(coro, loop_name):
        future: Future[str] = Future()
        future.set_result(f"scheduled:{loop_name}")
        coro.close()
        return future

    monkeypatch.setattr(
        "eclypse.remote.communication.interface.asyncio.run_coroutine_threadsafe",
        fake_schedule,
    )

    interface.connect()
    assert interface.connected is True
    assert interface.request_route("worker") == ("app", "svc", "worker")
    assert interface.get_neighbors() == ["app", "svc"]
    assert interface._handle_request("x").result() == "scheduled:loop"

    interface.disconnect()
    assert await interface._handle_request() == "offline"


@pytest.mark.asyncio
async def test_rest_and_mpi_interfaces_and_service_lifecycle(monkeypatch):
    monkeypatch.setattr(
        "eclypse.remote.communication.interface.ray_backend.get_actor",
        lambda name: SimpleNamespace(name=name),
    )

    rest_service = DemoRESTHandlers()
    rest = EclypseREST(rest_service)
    rest.connect()

    no_hop_route = Route(
        sender_id="sender",
        sender_node_id="edge-a",
        recipient_id="svc",
        recipient_node_id="edge-a",
        processing_time=0,
        hops=[],
    )
    remote_route = Route(
        sender_id="sender",
        sender_node_id="edge-a",
        recipient_id="svc",
        recipient_node_id="edge-b",
        processing_time=1,
        hops=[("edge-a", "edge-b", {"latency": 5, "bandwidth": 1000})],
    )

    assert await rest._not_connected_response() == (
        HTTPStatusCode.INTERNAL_SERVER_ERROR,
        {"message": "svc not connected"},
    )
    assert await rest._execute_request(
        "svc/hello",
        HTTPMethod.GET,
        no_hop_route,
        name="Ada",
    ) == (HTTPStatusCode.OK, {"name": "Ada"})
    assert await rest._execute_request("missing", HTTPMethod.GET, no_hop_route) == (
        HTTPStatusCode.NOT_FOUND,
        {"message": "Endpoint not found"},
    )
    assert await rest._execute_request("svc/hello", HTTPMethod.POST, no_hop_route) == (
        HTTPStatusCode.METHOD_NOT_ALLOWED,
        {"message": "Method not allowed"},
    )
    assert await rest._execute_request("svc/boom", HTTPMethod.POST, no_hop_route) == (
        HTTPStatusCode.INTERNAL_SERVER_ERROR,
        {"message": "boom"},
    )
    assert await rest._execute_request(
        "svc/bad-data", HTTPMethod.PUT, no_hop_route
    ) == (
        HTTPStatusCode.INTERNAL_SERVER_ERROR,
        {"message": "Invalid return type for handler: data must be a dictionary."},
    )
    assert await rest._execute_request(
        "svc/bad-code", HTTPMethod.DELETE, no_hop_route
    ) == (
        HTTPStatusCode.INTERNAL_SERVER_ERROR,
        {
            "message": "Invalid return type for handler: status code must be a valid HTTP code."
        },
    )
    assert (
        await rest._execute_request(
            "svc/hello", HTTPMethod.GET, remote_route, name="Bob"
        )
    )[0] is HTTPStatusCode.OK

    rest_service._run_task = object()
    with pytest.raises(ValueError, match="Must use a RESTService"):
        rest._handle_request(url="svc/hello", method=HTTPMethod.GET, route=no_hop_route)

    rest.disconnect()
    rest_service.event_loop.close()

    request_calls: list[tuple[str, HTTPMethod, dict[str, object], EclypseREST]] = []
    monkeypatch.setattr(
        "eclypse.remote.communication.rest.interface.HTTPRequest",
        lambda url, method, data, _rest: (
            request_calls.append((url, method, data, _rest))
            or {"url": url, "method": method, "data": data}
        ),
    )
    assert rest.get("svc/hello", name="Ada")["method"] is HTTPMethod.GET
    assert rest.post("svc/hello", name="Ada")["method"] is HTTPMethod.POST
    assert rest.put("svc/hello", name="Ada")["method"] is HTTPMethod.PUT
    assert rest.delete("svc/hello", name="Ada")["method"] is HTTPMethod.DELETE
    assert [call[1] for call in request_calls] == [
        HTTPMethod.GET,
        HTTPMethod.POST,
        HTTPMethod.PUT,
        HTTPMethod.DELETE,
    ]

    monkeypatch.setattr(
        "eclypse.remote.communication.rest.interface.EclypseCommunicationInterface._handle_request",
        lambda self, **kwargs: kwargs,
    )
    rest.service._run_task = None
    delegated = rest._handle_request(
        url="svc/hello", method=HTTPMethod.GET, route=no_hop_route
    )
    assert delegated["url"] == "svc/hello"

    async_service = AsyncRESTHandlers()
    async_rest = EclypseREST(async_service)
    async_rest.connect()
    assert await async_rest._execute_request(
        "svc/number",
        HTTPMethod.GET,
        no_hop_route,
    ) == (HTTPStatusCode.OK, {"ok": True})
    async_rest.disconnect()
    async_service.event_loop.close()

    duplicate_service = DuplicateRESTHandlers()
    duplicate_rest = EclypseREST(duplicate_service)
    with pytest.raises(ValueError, match="already registered"):
        duplicate_rest.connect()
    duplicate_service.event_loop.close()

    mpi_service = SimpleNamespace(
        application_id="app",
        id="svc",
        node=SimpleNamespace(manager_actor_name="edge-cloud/manager"),
        event_loop=asyncio.get_running_loop(),
    )
    mpi = EclypseMPI(mpi_service)

    with pytest.raises(ValueError, match="body must be a dictionary"):
        mpi.send("worker", "bad")  # type: ignore[arg-type]

    with pytest.raises(ValueError, match="body must be a dictionary"):
        mpi.bcast("bad")  # type: ignore[arg-type]

    monkeypatch.setattr(
        "eclypse.remote.communication.mpi.interface.UnicastRequest",
        lambda recipient_id, body, _mpi, timestamp=None: (
            "unicast",
            recipient_id,
            body,
            timestamp,
        ),
    )
    monkeypatch.setattr(
        "eclypse.remote.communication.mpi.interface.MulticastRequest",
        lambda recipient_ids, body, _mpi, timestamp=None: (
            "multicast",
            recipient_ids,
            body,
            timestamp,
        ),
    )
    monkeypatch.setattr(
        "eclypse.remote.communication.mpi.interface.BroadcastRequest",
        lambda body, _mpi, timestamp=None: ("broadcast", body, timestamp),
    )

    assert mpi.send("worker", {"x": 1})[:2] == ("unicast", "worker")
    assert mpi.send(["a", "b"], {"x": 1})[:2] == ("multicast", ["a", "b"])
    assert mpi.bcast({"x": 1})[:2] == ("broadcast", {"x": 1})
    assert (await mpi._not_connected_response()).code is ResponseCode.ERROR

    message_route = Route(
        sender_id="gateway",
        sender_node_id="edge-a",
        recipient_id="svc",
        recipient_node_id="edge-a",
        processing_time=0,
        hops=[],
    )
    response = await mpi._execute_request(message_route, payload=1)

    assert isinstance(response, Response)
    assert await mpi.recv() == {"payload": 1, "sender_id": "gateway"}

    with pytest.raises(ValueError, match="cannot send and broadcast"):
        exchange(send=True, broadcast=True)

    with pytest.raises(ValueError, match="must send, broadcast, or receive"):
        exchange()

    class EchoService:
        def __init__(self):
            self.mpi = SimpleNamespace(
                recv=lambda: asyncio.sleep(
                    0, result={"sender_id": "origin", "body": 2}
                ),
                send=lambda *args: asyncio.sleep(0, result=("sent", args)),
                bcast=lambda body: asyncio.sleep(0, result=("broadcast", body)),
            )

        @exchange(receive=True, send=True)
        async def forward(self, sender_id, message):
            return sender_id, {"echo": message["body"]}

        @exchange(broadcast=True)
        def fanout(self):
            return {"broadcast": True}

    echo = EchoService()

    assert await echo.forward() == ("sent", ("origin", {"echo": 2}))
    assert await echo.fanout() == ("broadcast", {"broadcast": True})

    service = DemoService("worker", store_step=True)
    node = SimpleNamespace(
        _logger=SimpleNamespace(bind=lambda **kwargs: kwargs),
        infrastructure_id="edge-cloud",
    )
    service.attach_node(node)
    service.application_id = "shop"

    assert service.full_id == "shop/worker"
    assert service.logger == {"id": "worker"}
    assert service.deployed is True

    rest_runtime = RESTService("frontend")
    rest_runtime.attach_node(node)

    with pytest.raises(RuntimeError, match="not mpi"):
        rest_runtime.mpi
