from __future__ import annotations

import asyncio
from types import SimpleNamespace

import pytest

from eclypse.simulation._simulator.local import (
    SimulationState,
    Simulator,
)
from eclypse.utils.constants import (
    START_EVENT,
    STOP_EVENT,
)


@pytest.mark.parametrize("shutdown_complete", [True, False])
def test_stop_racing_with_shutdown_closes_unscheduled_coroutine(
    monkeypatch, simulation_config, sample_infrastructure, shutdown_complete
):
    simulator = Simulator(sample_infrastructure, simulation_config)
    simulator._status = SimulationState.RUNNING
    simulator._finished.clear()
    loop = simulator._event_loop
    schedule = asyncio.run_coroutine_threadsafe
    coroutines = []

    def race_shutdown(coro, target_loop):
        coroutines.append(coro)
        if shutdown_complete:
            simulator._status = SimulationState.IDLE
            simulator._finished.set()
            target_loop.close()
            return schedule(coro, target_loop)
        raise RuntimeError("scheduler failed")

    monkeypatch.setattr(
        "eclypse.simulation._simulator.local.asyncio.run_coroutine_threadsafe",
        race_shutdown,
    )
    try:
        if shutdown_complete:
            simulator.stop()
        else:
            with pytest.raises(RuntimeError, match="scheduler failed"):
                simulator.stop()
        assert coroutines[0].cr_frame is None
        assert simulator._stop_requested is False
    finally:
        for coro in coroutines:
            coro.close()
        loop.close()


def test_wait_reports_write_failure_only_after_shutdown(
    simulation_config, sample_infrastructure
):
    simulator = Simulator(sample_infrastructure, simulation_config)
    simulator._reporter.error = "[json/service] Error during write: write boom"
    simulator._finished.clear()
    try:
        simulator.wait(timeout=0)
        simulator._finished.set()
        with pytest.raises(
            RuntimeError, match=r"Simulation report is incomplete.*write boom"
        ):
            simulator.wait(timeout=0)
    finally:
        simulator._event_loop.close()


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
@pytest.mark.parametrize("fail_during_shutdown", [False, True])
async def test_local_simulator_run_enqueues_stop_after_event_failures(
    monkeypatch,
    simulation_config,
    sample_infrastructure,
    fail_during_shutdown,
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
        if event_name == STOP_EVENT and fail_during_shutdown:
            raise RuntimeError("shutdown failed")

    async def fake_sleep(_: float):
        lifecycle.append(("sleep", None))

    printed: list[tuple[str, str]] = []
    simulator._events_queue = FakeQueue()
    simulator._reporter = SimpleNamespace(start=start, stop=stop)
    simulator.enqueue_event = fake_enqueue  # type: ignore[method-assign]
    simulator.fire = fake_fire  # type: ignore[method-assign]
    monkeypatch.setattr(
        "eclypse.simulation._simulator.local.print_exception",
        lambda exc, origin, _logger: printed.append((str(exc), origin)),
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
    assert printed == [("boom", "Simulator")] + (
        [("shutdown failed", "Simulator")] if fail_during_shutdown else []
    )
    assert lifecycle.count(("enqueue", (STOP_EVENT, None))) == 1
    assert lifecycle[-1] == ("stop", None)
