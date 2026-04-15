from __future__ import annotations

import asyncio
from collections import deque
from datetime import (
    datetime,
    timedelta,
)
from types import SimpleNamespace
from typing import Any

import pytest

from eclypse.remote.communication.mpi.requests import (
    BroadcastRequest,
    MulticastRequest,
    UnicastRequest,
)
from eclypse.remote.communication.request import (
    EclypseRequest,
    RouteNotFoundError,
)
from eclypse.remote.service.rest import RESTService
from eclypse.remote.service.service import (
    Service,
    _start_loop,
)


class ScriptedService(Service):
    def __init__(self, service_id: str, script: list[Any], **kwargs):
        super().__init__(service_id, **kwargs)
        self.script = deque(script)
        self.deploy_calls = 0
        self.undeploy_calls = 0

    async def step(self):
        action = self.script.popleft()
        if not self.script:
            self._running = False
        if isinstance(action, Exception):
            raise action
        return action

    def on_deploy(self):
        self.deploy_calls += 1

    def on_undeploy(self):
        self.undeploy_calls += 1


class FakeThread:
    def __init__(self, target=None, args=()):
        self.target = target
        self.args = args
        self.started = False
        self.joined = False

    def start(self):
        self.started = True

    def join(self):
        self.joined = True


class FakeLoop:
    def __init__(self):
        self.created: list[tuple[Any, str | None]] = []
        self.calls: list[tuple[Any, tuple[Any, ...]]] = []
        self.closed = False
        self.stopped = False
        self.runtime_error: Exception | None = None
        self.run_task: Any = None
        self.forever = False

    def create_task(self, coro, name=None):
        coro.close()
        task = SimpleNamespace(name=name, cancelled=False)

        def cancel():
            task.cancelled = True

        task.cancel = cancel
        self.created.append((task, name))
        return task

    def call_soon_threadsafe(self, callback, *args):
        self.calls.append((callback, args))
        callback(*args)

    def stop(self):
        self.stopped = True

    def close(self):
        self.closed = True

    def run_until_complete(self, task):
        self.run_task = task
        if self.runtime_error is not None:
            raise self.runtime_error

    def run_forever(self):
        self.forever = True
        if self.runtime_error is not None:
            raise self.runtime_error


class FakeComm:
    def __init__(self, service):
        self.service = service
        self.connected = False
        self.disconnected = False

    def connect(self):
        self.connected = True

    def disconnect(self):
        self.disconnected = True


class DummyRESTRuntime(RESTService):
    async def step(self):
        return None


def _make_node(dummy_logger):
    return SimpleNamespace(_logger=dummy_logger, infrastructure_id="edge-cloud")


def test_service_guard_properties_and_basic_accessors(dummy_logger):
    with pytest.raises(ValueError, match="Invalid communication interface"):
        Service("broken", communication_interface="grpc")  # type: ignore[arg-type]

    service = ScriptedService("worker", [1], store_step=True)

    with pytest.raises(RuntimeError, match="not deployed on any node"):
        service.mpi
    with pytest.raises(RuntimeError, match="not deployed on any node"):
        service.rest
    with pytest.raises(RuntimeError, match="not deployed on any node"):
        service.event_loop
    with pytest.raises(RuntimeError, match="not deployed on any node"):
        service.node
    with pytest.raises(ValueError, match="Application ID not set"):
        service.full_id
    with pytest.raises(NotImplementedError, match="must be overridden"):
        asyncio.run(Service("base").step())

    node = _make_node(dummy_logger)
    service.attach_node(node)
    service.application_id = "shop"
    service._comm = SimpleNamespace(name="mpi")
    service._loop = asyncio.new_event_loop()
    try:
        assert service.infrastructure_id == "edge-cloud"
        assert service.full_id == "shop/worker"
        assert service.id == "worker"
        assert service.application_id == "shop"
        assert service.deployed is True
        assert service.running is False
        assert service.step_count == 0
        assert service.logger is dummy_logger
        assert service.mpi.name == "mpi"
    finally:
        service.event_loop.close()

    rest_service = DummyRESTRuntime("frontend")
    rest_service.attach_node(node)
    rest_service._comm = SimpleNamespace(name="rest")
    assert rest_service.rest.name == "rest"
    with pytest.raises(RuntimeError, match="not mpi"):
        rest_service.mpi
    assert asyncio.run(rest_service.step()) is None
    rest_service.detach_node()

    service.detach_node()
    assert service.deployed is False


@pytest.mark.asyncio
async def test_service_run_handles_missing_routes_and_stored_steps(dummy_logger):
    node = _make_node(dummy_logger)

    service = ScriptedService(
        "worker",
        [RouteNotFoundError("catalog"), None, 7],
        store_step=True,
    )
    service.attach_node(node)
    service._running = True

    await service.run()

    assert service.step_count == 3
    assert list(service._step_queue) == [7]
    assert any(
        "route to catalog was not found" in record[1][0]
        for record in dummy_logger.records
        if record[0] == "warning"
    )


def test_service_deploy_start_stop_and_undeploy_flow(monkeypatch, dummy_logger):
    service = ScriptedService("worker", [1], store_step=True)
    fake_loop = FakeLoop()
    fake_thread = FakeThread()
    comms: list[FakeComm] = []

    monkeypatch.setattr(
        "eclypse.remote.service.service.asyncio.new_event_loop",
        lambda: fake_loop,
    )
    monkeypatch.setattr(
        "eclypse.remote.service.service.threading.Thread",
        lambda target, args: fake_thread,
    )
    monkeypatch.setattr(
        "eclypse.remote.service.service.EclypseMPI",
        lambda runtime_service: comms.append(FakeComm(runtime_service)) or comms[-1],
    )

    node = _make_node(dummy_logger)

    with pytest.raises(RuntimeError, match="not deployed on any node"):
        service._start()
    with pytest.raises(RuntimeError, match="not deployed on any node"):
        service._stop()
    with pytest.raises(RuntimeError, match="not deployed on any node"):
        service._undeploy()

    service._deploy(node)

    assert service.deploy_calls == 1
    assert service.deployed is True
    assert service.event_loop is fake_loop
    assert fake_loop.created[0][1] == "task-worker"
    assert service._thread is fake_thread

    with pytest.raises(RuntimeError, match="already deployed"):
        service._deploy(node)

    service._start()

    assert isinstance(service._comm, FakeComm)
    assert service._comm.connected is True
    assert service.running is True
    assert fake_thread.started is True

    with pytest.raises(RuntimeError, match="cannot be undeployed"):
        service._undeploy()

    service._stop()

    assert service.running is False
    assert service._run_task.cancelled is True
    assert fake_loop.stopped is True
    assert fake_thread.joined is True

    service._undeploy()

    assert service.undeploy_calls == 1
    assert comms[0].disconnected is True
    assert service.deployed is False
    assert service._comm is None
    assert service._loop is None
    assert service._run_task_fn is None
    assert service._run_task is None
    assert service._thread is None


def test_rest_service_specific_lifecycle(monkeypatch, dummy_logger):
    service = DummyRESTRuntime("frontend")
    node = _make_node(dummy_logger)
    fake_loop = FakeLoop()
    fake_thread = FakeThread()
    comms: list[FakeComm] = []

    monkeypatch.setattr(
        "eclypse.remote.service.service.asyncio.new_event_loop",
        lambda: fake_loop,
    )
    monkeypatch.setattr(
        "eclypse.remote.service.service.threading.Thread",
        lambda target, args: fake_thread,
    )
    monkeypatch.setattr(
        "eclypse.remote.service.service.EclypseREST",
        lambda runtime_service: comms.append(FakeComm(runtime_service)) or comms[-1],
    )

    with pytest.raises(RuntimeError, match="not deployed on any node"):
        service._stop()

    service._deploy(node)

    assert service._run_task is None
    assert service._thread is fake_thread

    service._start()
    assert comms[0].connected is True
    assert service.running is True

    service._stop()
    assert service.running is False
    assert fake_loop.stopped is True
    assert fake_thread.joined is True


def test_start_loop_handles_forever_cancelled_and_error_paths(monkeypatch):
    set_loops: list[FakeLoop] = []
    printed: list[tuple[str, str]] = []

    monkeypatch.setattr(
        "eclypse.remote.service.service.asyncio.set_event_loop",
        lambda loop: set_loops.append(loop),
    )
    monkeypatch.setattr(
        "eclypse.remote.service.service.print_exception",
        lambda exc, label: printed.append((str(exc), label)),
    )

    normal_loop = FakeLoop()
    normal_comm = FakeComm(None)
    normal_service = SimpleNamespace(
        id="svc",
        event_loop=normal_loop,
        _run_task="task",
        _comm=normal_comm,
    )
    _start_loop(normal_service)
    assert normal_loop.run_task == "task"
    assert normal_loop.closed is True
    assert normal_comm.disconnected is True

    forever_loop = FakeLoop()
    forever_service = SimpleNamespace(
        id="svc",
        event_loop=forever_loop,
        _run_task=None,
        _comm=None,
    )
    _start_loop(forever_service)
    assert forever_loop.forever is True
    assert forever_loop.closed is True

    cancelled_loop = FakeLoop()
    cancelled_loop.runtime_error = asyncio.CancelledError()
    cancelled_service = SimpleNamespace(
        id="svc",
        event_loop=cancelled_loop,
        _run_task="task",
        _comm=None,
    )
    _start_loop(cancelled_service)

    stopped_loop = FakeLoop()
    stopped_loop.runtime_error = RuntimeError(
        "Event loop stopped before Future completed."
    )
    stopped_service = SimpleNamespace(
        id="svc",
        event_loop=stopped_loop,
        _run_task="task",
        _comm=None,
    )
    _start_loop(stopped_service)

    runtime_loop = FakeLoop()
    runtime_loop.runtime_error = RuntimeError("boom")
    runtime_service = SimpleNamespace(
        id="svc",
        event_loop=runtime_loop,
        _run_task="task",
        _comm=None,
    )
    _start_loop(runtime_service)

    generic_loop = FakeLoop()
    generic_loop.runtime_error = ValueError("bad")
    generic_service = SimpleNamespace(
        id="svc",
        event_loop=generic_loop,
        _run_task="task",
        _comm=None,
    )
    _start_loop(generic_service)

    assert len(set_loops) == 6
    assert printed == [("boom", "svc"), ("bad", "svc")]


def test_request_wrappers_and_properties(monkeypatch):
    await_calls: list[str] = []

    async def awaited_value():
        await_calls.append("awaited")
        return "done"

    monkeypatch.setattr(
        "eclypse.remote.communication.request.EclypseRequest.__await__",
        lambda self: awaited_value().__await__(),
    )

    request = object.__new__(EclypseRequest)
    request._data = {"payload": 1}
    request._timestamp = datetime(2026, 1, 1, 0, 0, 0)
    request._recipient_ids = ["a", "b"]
    request._routes = [
        SimpleNamespace(done=lambda: True, result=lambda: "route-a"),
        SimpleNamespace(done=lambda: False),
    ]
    request._futures = [
        SimpleNamespace(
            done=lambda: True,
            result=lambda: {
                "future": "response-a",
                "timestamp": datetime(2026, 1, 1, 0, 0, 5),
            },
        ),
        SimpleNamespace(done=lambda: False),
    ]

    assert request.data == {"payload": 1}
    assert request.recipient_ids == ["a", "b"]
    assert request.routes == ["route-a", None]
    assert request.responses == ["response-a", None]
    assert request.elapsed_times == [timedelta(seconds=5), None]
    assert asyncio.run(_consume(request)) == "done"
    assert await_calls == ["awaited"]

    def fake_eclypse_init(self, recipient_ids, data, _comm, timestamp=None):
        self._recipient_ids = recipient_ids
        self._data = data
        self._comm = _comm
        self._timestamp = timestamp

    monkeypatch.setattr(
        "eclypse.remote.communication.mpi.requests.multicast.EclypseRequest.__init__",
        fake_eclypse_init,
    )
    monkeypatch.setattr(
        "eclypse.remote.communication.mpi.requests.broadcast.ray_backend.get",
        lambda neighbors: ["a", "b"] if neighbors == "neighbors-ref" else neighbors,
    )

    mpi = SimpleNamespace(get_neighbors=lambda: "neighbors-ref")

    multicast = MulticastRequest(
        ["a", "b"], {"value": 1}, mpi, timestamp=datetime(2026, 1, 1)
    )
    unicast = UnicastRequest("worker", {"value": 2}, mpi)
    unicast._routes = [SimpleNamespace(done=lambda: True, result=lambda: "route")]
    unicast._futures = [
        SimpleNamespace(
            done=lambda: True,
            result=lambda: {
                "future": "response",
                "timestamp": datetime(2026, 1, 1, 0, 0, 3),
            },
        )
    ]
    unicast._timestamp = datetime(2026, 1, 1, 0, 0, 0)
    broadcast = BroadcastRequest({"value": 3}, mpi)

    assert multicast.recipient_ids == ["a", "b"]
    assert asyncio.run(_consume(multicast)) == "done"
    assert unicast.recipient_id == "worker"
    assert unicast.route == "route"
    assert unicast.response == "response"
    assert unicast.elapsed_time == timedelta(seconds=3)
    assert asyncio.run(_consume(unicast)) == "done"
    assert broadcast.recipient_ids == ["a", "b"]
    assert asyncio.run(_consume(broadcast)) == "done"


async def _consume(obj):
    return await obj
