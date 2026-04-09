from __future__ import annotations

import asyncio
from concurrent.futures import Future
from types import SimpleNamespace
from typing import Any

import pytest

from eclypse.remote._node.node import RemoteNode
from eclypse.remote._node.ops_thread import RemoteOpsThread
from eclypse.remote.communication.mpi import EclypseMPI
from eclypse.remote.communication.rest import EclypseREST
from eclypse.remote.utils import (
    RemoteOps,
    ResponseCode,
)


class DemoNode(RemoteNode):
    def build(self, **node_config):
        self.node_config = node_config


class FakeOpsThread:
    def __init__(self, node: RemoteNode, loop: asyncio.AbstractEventLoop):
        self.node = node
        self.loop = loop
        self.started = False
        self.calls: list[tuple[Any, dict[str, Any]]] = []

    def start(self):
        self.started = True

    def submit(self, engine_op: RemoteOps, op_args: dict[str, Any]):
        self.calls.append((engine_op, op_args))
        future = self.loop.create_future()
        future.set_result(
            {
                "operation": engine_op,
                "args": op_args,
            }
        )
        return future


class FakeThreadPoolExecutor:
    def submit(self, fn, param, **kwargs):
        future: Future[Any] = Future()
        future.set_result(fn(param, **kwargs))
        return future


class LoopStub:
    def __init__(self):
        self.future = object()
        self.threadsafe_calls: list[tuple[Any, tuple[Any, ...]]] = []

    def create_future(self):
        return self.future

    def call_soon_threadsafe(self, callback, *args):
        self.threadsafe_calls.append((callback, args))
        callback(*args)


@pytest.mark.asyncio
async def test_remote_node_build_entrypoints_and_actor_cache(monkeypatch, dummy_logger):
    loop = asyncio.get_running_loop()
    actor_calls: list[str] = []

    monkeypatch.setattr(
        "eclypse.remote._node.node.asyncio.get_event_loop", lambda: loop
    )
    monkeypatch.setattr("eclypse.remote._node.node.RemoteOpsThread", FakeOpsThread)
    monkeypatch.setattr(
        "eclypse.remote._node.node.ThreadPoolExecutor",
        FakeThreadPoolExecutor,
    )
    monkeypatch.setattr("eclypse.remote._node.node.config_logger", lambda: None)
    monkeypatch.setattr("eclypse.remote._node.node.logger", dummy_logger)
    monkeypatch.setattr(
        "eclypse.remote._node.node.ray_backend.get_actor",
        lambda actor_name: actor_calls.append(actor_name) or {"actor": actor_name},
    )

    node = DemoNode("edge-a", "edge-cloud", cpu=8)

    assert node.node_config == {"cpu": 8}
    assert node.id == "edge-a"
    assert node.infrastructure_id == "edge-cloud"
    assert node.manager_actor_name == "edge-cloud/manager"
    assert repr(node) == "edge-a"
    assert node.engine_loop is loop
    assert node._engine_ops_thread.started is True

    ops_result = await node.ops_entrypoint(RemoteOps.DEPLOY, service_id="svc")
    local_result = await node.entrypoint(
        None,
        lambda target, value: f"{target.id}:{value}",
        value=3,
    )
    node.services["worker"] = SimpleNamespace(name="worker")
    service_result = await node.entrypoint(
        "worker",
        lambda target, value: f"{target.name}:{value}",
        value=5,
    )

    mpi_calls: list[tuple[str, str]] = []
    rest_calls: list[tuple[str, str]] = []

    async def handle_mpi(*_, **__):
        mpi_calls.append(("mpi", "called"))
        return "mpi-response"

    async def handle_rest(*_, **__):
        rest_calls.append(("rest", "called"))
        return "rest-response"

    node.services["svc"] = SimpleNamespace(
        mpi=SimpleNamespace(_handle_request=handle_mpi),
        rest=SimpleNamespace(_handle_request=handle_rest),
    )
    route = SimpleNamespace(recipient_id="svc")

    assert ops_result["operation"] is RemoteOps.DEPLOY
    assert local_result == "edge-a:3"
    assert service_result == "worker:5"
    assert await node.service_comm_entrypoint(route, EclypseMPI) == "mpi-response"
    assert await node.service_comm_entrypoint(route, EclypseREST) == "rest-response"
    assert mpi_calls == [("mpi", "called")]
    assert rest_calls == [("rest", "called")]

    with pytest.raises(ValueError, match="Invalid communication interface"):
        await node.service_comm_entrypoint(route, object)  # type: ignore[arg-type]

    first_actor = node.get_actor("edge-cloud/manager")
    second_actor = node.get_actor("edge-cloud/manager")

    assert first_actor == second_actor
    assert actor_calls == ["edge-cloud/manager"]
    assert node.logger is dummy_logger


def test_remote_ops_thread_submit_and_operation_results():
    node = SimpleNamespace(id="edge-a", services={})
    loop = LoopStub()
    ops_thread = RemoteOpsThread(node, loop)

    future = ops_thread.submit(RemoteOps.START, {"service_id": "svc"})
    queued_engine_op, queued_args, queued_future = ops_thread.ops_queue.get_nowait()

    assert future is loop.future
    assert queued_engine_op is RemoteOps.START
    assert queued_args == {"service_id": "svc"}
    assert queued_future is future

    service = SimpleNamespace(
        _deploy=lambda deployed_node: setattr(service, "deployed_node", deployed_node),
        _undeploy=lambda: setattr(service, "undeployed", True),
        _start=lambda: setattr(service, "started", True),
        _stop=lambda: setattr(service, "stopped", True),
    )

    deploy_result = ops_thread.deploy("svc", service)
    start_result = ops_thread.start_service("svc")
    stop_result = ops_thread.stop_service("svc")
    undeploy_result = ops_thread.undeploy("svc")

    assert deploy_result.code is ResponseCode.OK
    assert deploy_result.service_id == "svc"
    assert start_result.operation is RemoteOps.START
    assert stop_result.operation is RemoteOps.STOP
    assert undeploy_result.operation is RemoteOps.UNDEPLOY
    assert undeploy_result.service is service
    assert node.services == {}

    failing_service = SimpleNamespace(
        _deploy=lambda *_args: (_ for _ in ()).throw(RuntimeError("deploy failed")),
        _undeploy=lambda: (_ for _ in ()).throw(RuntimeError("undeploy failed")),
        _start=lambda: (_ for _ in ()).throw(RuntimeError("start failed")),
        _stop=lambda: (_ for _ in ()).throw(RuntimeError("stop failed")),
    )
    node.services["broken"] = failing_service

    assert ops_thread.deploy("broken", failing_service).error == "deploy failed"
    assert ops_thread.start_service("broken").error == "start failed"
    assert ops_thread.stop_service("broken").error == "stop failed"
    assert ops_thread.undeploy("broken").error == "undeploy failed"


@pytest.mark.asyncio
async def test_remote_ops_thread_run_and_set_future_result(monkeypatch):
    loop = asyncio.get_running_loop()
    node = SimpleNamespace(id="edge-a", services={})
    ops_thread = RemoteOpsThread(node, loop)
    result_future = loop.create_future()
    service = object()
    scheduled: list[Any] = []
    queue_items = iter(
        [
            (
                RemoteOps.DEPLOY,
                {"service_id": "svc", "service": service},
                result_future,
            ),
        ]
    )

    monkeypatch.setattr(
        ops_thread,
        "deploy",
        lambda **kwargs: {"status": "ok", "kwargs": kwargs},
    )
    monkeypatch.setattr(
        ops_thread.ops_queue,
        "get",
        lambda: next(queue_items),
    )

    def fake_run_coroutine_threadsafe(coro, _loop):
        scheduled.append(loop.create_task(coro))
        raise StopIteration

    monkeypatch.setattr(
        "eclypse.remote._node.ops_thread.asyncio.run_coroutine_threadsafe",
        fake_run_coroutine_threadsafe,
    )

    with pytest.raises(StopIteration):
        ops_thread.run()

    assert len(scheduled) == 1
    await scheduled[0]
    assert result_future.result() == {
        "status": "ok",
        "kwargs": {"service_id": "svc", "service": service},
    }

    second_future = loop.create_future()
    await ops_thread.set_future_result(second_future, "done")
    assert second_future.result() == "done"
