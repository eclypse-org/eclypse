from __future__ import annotations

import asyncio
from types import SimpleNamespace

import pytest

from eclypse.simulation._simulator.local import (
    SimulationState,
    Simulator,
)
from eclypse.simulation._simulator.ops_handler import (
    RemoteSimOpsHandler,
    _handle_error,
)
from eclypse.simulation._simulator.remote import RemoteSimulator
from eclypse.simulation.simulation import (
    Simulation,
    _local_remote_event_call,
)
from eclypse.utils.constants import (
    START_EVENT,
    STOP_EVENT,
)


def test_local_remote_event_call_uses_matching_dispatch():
    calls: list[tuple[str, tuple, dict]] = []
    local = SimpleNamespace(
        start=lambda *args, **kwargs: calls.append(("local", args, kwargs))
    )
    remote = SimpleNamespace(
        start=SimpleNamespace(
            remote=lambda *args, **kwargs: calls.append(("remote", args, kwargs))
        )
    )

    _local_remote_event_call(local, None, "start", 1, value=2)
    _local_remote_event_call(remote, object(), "start", 3, value=4)

    assert calls == [
        ("local", (1,), {"value": 2}),
        ("remote", (3,), {"value": 4}),
    ]


def test_simulation_register_start_step_stop_and_report(
    monkeypatch,
    sample_infrastructure,
    sample_application,
    simulation_config,
    static_strategy,
):
    event_calls: list[tuple[str, tuple, dict]] = []

    monkeypatch.setattr(
        "eclypse.simulation.simulation._local_remote_event_call",
        lambda sim, remote, fn, *args, **kwargs: event_calls.append((fn, args, kwargs)),
    )
    report_calls: list[tuple] = []
    monkeypatch.setattr(
        "eclypse.simulation.simulation.Report",
        lambda *args: report_calls.append(args) or "report-object",
    )

    simulation = Simulation(sample_infrastructure, simulation_config)
    simulation.register(sample_application, static_strategy)
    simulation.start()
    simulation.step()
    simulation.stop(blocking=False)

    assert sample_application.id in simulation.applications
    assert event_calls[0][0] == "start"
    assert event_calls[1][0] == "trigger"
    assert simulation.report == "report-object"
    assert report_calls
    assert simulation.path == simulation_config.path


@pytest.mark.asyncio
async def test_local_simulator_fire_and_finalize(
    simulation_config, sample_infrastructure
):
    simulator = Simulator(sample_infrastructure, simulation_config)
    metric = SimpleNamespace(
        _fire=lambda trigger_event: None,
        is_metric=True,
        name="metric",
    )
    trigger_event = SimpleNamespace(name="drive", n_calls=4)
    simulator._events["metric"] = metric  # type: ignore[index]
    simulator._events["drive"] = trigger_event  # type: ignore[index]
    report_calls: list[tuple[str, int, object]] = []

    async def report(**kwargs):
        report_calls.append(
            (kwargs["event_name"], kwargs["event_idx"], kwargs["callback"])
        )

    async def stop():
        return None

    simulator._reporter = SimpleNamespace(report=report, stop=stop)

    await simulator.fire("metric", "drive")
    await simulator._finalize_shutdown()

    assert report_calls == [("drive", 4, metric)]
    assert simulator.status is SimulationState.IDLE


@pytest.mark.asyncio
async def test_local_simulator_fire_skips_reporting_for_non_metric_callbacks(
    simulation_config,
    sample_infrastructure,
):
    simulator = Simulator(sample_infrastructure, simulation_config)
    fired: list[object] = []
    event = SimpleNamespace(
        _fire=lambda trigger_event: fired.append(trigger_event),
        is_metric=False,
    )
    trigger_event = SimpleNamespace(name="drive", n_calls=2)
    report_calls: list[dict[str, object]] = []

    async def report(**kwargs):
        report_calls.append(kwargs)

    simulator._events["metricless"] = event  # type: ignore[index]
    simulator._events["drive"] = trigger_event  # type: ignore[index]
    simulator._reporter = SimpleNamespace(report=report)

    await simulator.fire("metricless", "drive")

    assert fired == [trigger_event]
    assert report_calls == []


@pytest.mark.asyncio
async def test_local_simulator_run_handles_timeout_and_shutdown(
    monkeypatch,
    simulation_config,
    sample_infrastructure,
):
    simulator = Simulator(sample_infrastructure, simulation_config)
    lifecycle: list[tuple[str, object]] = []
    simulator._status = SimulationState.RUNNING
    simulator._events = {
        "tick": SimpleNamespace(name="tick", _trigger=lambda *_: False)
    }
    simulator._events_queue = SimpleNamespace(
        empty=lambda: True,
        get=lambda: asyncio.sleep(0),
    )

    async def start(loop):
        lifecycle.append(("start", loop))

    async def stop():
        lifecycle.append(("stop", None))

    async def fake_enqueue(event_name: str, triggered_by: str | None = None):
        lifecycle.append(("enqueue", (event_name, triggered_by)))

    async def fake_sleep(_: float):
        lifecycle.append(("sleep", None))

    async def fake_wait_for(awaitable, timeout):
        lifecycle.append(("wait_for", timeout))
        awaitable.close()
        simulator._status = SimulationState.STOPPING
        raise TimeoutError

    simulator._reporter = SimpleNamespace(start=start, stop=stop)
    simulator.enqueue_event = fake_enqueue  # type: ignore[method-assign]
    monkeypatch.setattr(
        "eclypse.simulation._simulator.local.asyncio.wait_for",
        fake_wait_for,
    )
    monkeypatch.setattr(
        "eclypse.simulation._simulator.local.asyncio.sleep",
        fake_sleep,
    )

    await simulator.run()

    assert lifecycle[0][0] == "start"
    assert ("enqueue", (START_EVENT, None)) in lifecycle
    assert any(item[0] == "wait_for" for item in lifecycle)
    assert lifecycle[-1] == ("stop", None)


@pytest.mark.asyncio
async def test_local_simulator_run_enqueues_stop_after_event_failures(
    monkeypatch,
    simulation_config,
    sample_infrastructure,
):
    simulator = Simulator(sample_infrastructure, simulation_config)
    simulator._status = SimulationState.RUNNING
    lifecycle: list[tuple[str, object]] = []
    queue_items = [{"event_name": "periodic", "triggered_by": None}]
    trigger_state = {"count": 0}

    def periodic_trigger(_trigger_event=None):
        if _trigger_event is None and trigger_state["count"] == 0:
            trigger_state["count"] += 1
            return True
        return False

    simulator._events = {
        "periodic": SimpleNamespace(name="periodic", _trigger=periodic_trigger),
        STOP_EVENT: SimpleNamespace(name=STOP_EVENT, _trigger=lambda *_: False),
    }

    class FakeQueue:
        def empty(self):
            return not queue_items

        async def get(self):
            return queue_items.pop(0)

        def get_nowait(self):
            return queue_items.pop(0)

    async def start(_loop):
        lifecycle.append(("start", None))

    async def stop():
        lifecycle.append(("stop", None))

    async def fake_enqueue(event_name: str, triggered_by: str | None = None):
        lifecycle.append(("enqueue", (event_name, triggered_by)))
        if event_name == STOP_EVENT:
            simulator._status = SimulationState.STOPPING
            queue_items.append({"event_name": STOP_EVENT, "triggered_by": None})

    async def fake_fire(event_name: str, triggered_by: str | None = None):
        lifecycle.append(("fire", (event_name, triggered_by)))
        if event_name == "periodic":
            raise RuntimeError("boom")

    async def fake_sleep(_: float):
        lifecycle.append(("sleep", None))

    printed: list[tuple[str, str]] = []
    simulator._events_queue = FakeQueue()
    simulator._reporter = SimpleNamespace(start=start, stop=stop)
    simulator.enqueue_event = fake_enqueue  # type: ignore[method-assign]
    simulator.fire = fake_fire  # type: ignore[method-assign]
    monkeypatch.setattr(
        "eclypse.simulation._simulator.local.print_exception",
        lambda exc, origin: printed.append((str(exc), origin)),
    )
    monkeypatch.setattr(
        "eclypse.simulation._simulator.local.asyncio.sleep",
        fake_sleep,
    )

    await simulator.run()

    assert ("enqueue", (START_EVENT, None)) in lifecycle
    assert ("enqueue", ("periodic", None)) in lifecycle
    assert ("enqueue", (STOP_EVENT, None)) in lifecycle
    assert ("fire", ("periodic", None)) in lifecycle
    assert ("fire", (STOP_EVENT, None)) in lifecycle
    assert printed == [("boom", "Simulator")]
    assert lifecycle[-1] == ("stop", None)


def test_remote_ops_handler_formats_errors(service_with_results):
    ok = SimpleNamespace(
        code=SimpleNamespace(name="OK"),
        operation=SimpleNamespace(name="DEPLOY"),
        node_id="edge-a",
        service_id="gateway",
        error=None,
        service=None,
    )
    error = SimpleNamespace(
        code=SimpleNamespace(name="ERROR"),
        operation=SimpleNamespace(name="STOP"),
        node_id="edge-b",
        service_id="worker",
        error="boom",
        service=service_with_results,
    )

    _handle_error([ok])

    with pytest.raises(ValueError, match="STOP failed on node 'edge-b'"):
        _handle_error([ok, error])


@pytest.mark.asyncio
async def test_remote_simulator_route_and_cleanup(
    monkeypatch,
    sample_infrastructure,
    sample_application,
    simulation_config,
):
    simulator = RemoteSimulator(
        sample_infrastructure,
        simulation_config,
        remotes=[],
    )
    simulator.register(sample_application)
    simulator.placements["shop"].mapping = {"gateway": "edge-a", "worker": "edge-b"}

    stop_calls: list[str] = []
    undeploy_calls: list[str] = []
    monkeypatch.setattr(
        RemoteSimOpsHandler,
        "stop",
        lambda placement: stop_calls.append(placement.application.id),
    )
    monkeypatch.setattr(
        RemoteSimOpsHandler,
        "undeploy",
        lambda placement: undeploy_calls.append(placement.application.id),
    )
    simulator.placements["shop"].mark_deployed()

    route = await simulator.route("shop", "gateway", "worker")
    neighbors = await simulator.get_neighbors("shop", "gateway")
    simulator.cleanup()

    assert simulator.remote is True
    assert simulator.id.endswith("/manager")
    assert simulator.get_status() is simulator.status
    assert neighbors == ["worker"]
    assert route is not None
    assert route.sender_node_id == "edge-a"
    assert stop_calls == ["shop"]
    assert undeploy_calls == ["shop"]


def test_remote_simulator_enact_coordinates_remote_operations(
    monkeypatch,
    sample_infrastructure,
    simulation_config,
):
    simulator = RemoteSimulator(
        sample_infrastructure,
        simulation_config,
        remotes=[],
    )
    reset = SimpleNamespace(
        reset_requested=True,
        deployed=True,
        mapping={"gateway": "edge-a"},
        application=SimpleNamespace(id="reset"),
    )
    fresh = SimpleNamespace(
        reset_requested=False,
        deployed=False,
        mapping={"gateway": "edge-b"},
        application=SimpleNamespace(id="fresh"),
    )
    idle = SimpleNamespace(
        reset_requested=False,
        deployed=False,
        mapping={},
        application=SimpleNamespace(id="idle"),
    )
    simulator._manager = SimpleNamespace(placements={"a": reset, "b": fresh, "c": idle})

    calls: list[tuple[str, str]] = []
    monkeypatch.setattr(
        RemoteSimOpsHandler,
        "stop",
        lambda placement: calls.append(("stop", placement.application.id)),
    )
    monkeypatch.setattr(
        RemoteSimOpsHandler,
        "undeploy",
        lambda placement: calls.append(("undeploy", placement.application.id)),
    )
    monkeypatch.setattr(
        RemoteSimOpsHandler,
        "deploy",
        lambda placement: calls.append(("deploy", placement.application.id)),
    )
    monkeypatch.setattr(
        RemoteSimOpsHandler,
        "start",
        lambda placement: calls.append(("start", placement.application.id)),
    )
    monkeypatch.setattr(
        "eclypse.simulation._simulator.remote.Simulator.enact",
        lambda self: calls.append(("super", "enact")),
    )

    simulator.enact()

    assert calls == [
        ("stop", "reset"),
        ("undeploy", "reset"),
        ("deploy", "fresh"),
        ("start", "fresh"),
        ("super", "enact"),
    ]


@pytest.mark.asyncio
async def test_remote_simulator_wait_finalize_and_route_edge_cases(
    monkeypatch,
    sample_infrastructure,
    sample_application,
    simulation_config,
):
    simulator = RemoteSimulator(
        sample_infrastructure,
        simulation_config,
        remotes=[],
    )
    simulator.register(sample_application)
    simulator.placements["shop"].mapping = {"gateway": "edge-a"}

    calls: list[tuple[str, object]] = []

    async def fake_to_thread(fn, timeout):
        calls.append(("wait", timeout))
        assert fn.__self__ is simulator

    async def fake_super_finalize(self):
        calls.append(("super-finalize", self))

    monkeypatch.setattr(
        "eclypse.simulation._simulator.remote.asyncio.to_thread",
        fake_to_thread,
    )
    monkeypatch.setattr(
        "eclypse.simulation._simulator.remote.Simulator._finalize_shutdown",
        fake_super_finalize,
    )
    monkeypatch.setattr(simulator, "cleanup", lambda: calls.append(("cleanup", None)))

    await simulator.wait(timeout=1.25)
    await simulator._finalize_shutdown()

    assert await simulator.route("shop", "gateway", "gateway") is None
    assert await simulator.route("shop", "gateway", "worker") is None

    simulator.placements["shop"].mapping = {
        "gateway": "edge-a",
        "worker": "edge-a",
    }
    same_node = await simulator.route("shop", "gateway", "worker")
    assert same_node is not None
    assert same_node.hops == []

    simulator.placements["shop"].mapping = {
        "gateway": "edge-a",
        "worker": "edge-b",
    }
    monkeypatch.setattr(sample_infrastructure, "path", lambda *_args: None)
    assert await simulator.route("shop", "gateway", "worker") is None

    assert calls[0] == ("wait", 1.25)
    assert calls[1][0] == "cleanup"
    assert calls[2] == ("super-finalize", simulator)
