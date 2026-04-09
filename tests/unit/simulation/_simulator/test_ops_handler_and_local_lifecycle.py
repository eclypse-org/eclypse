from __future__ import annotations

import asyncio
from types import SimpleNamespace

import pytest

from eclypse.remote.utils import (
    RemoteOpResult,
    RemoteOps,
    ResponseCode,
)
from eclypse.simulation._simulator.local import (
    SimulationState,
    Simulator,
    _run_loop,
)
from eclypse.simulation._simulator.ops_handler import RemoteSimOpsHandler


def test_remote_ops_handler_get_remotes_caches_actor_lookup(
    monkeypatch,
    colocated_placement,
):
    actor_names: list[str] = []
    actor = SimpleNamespace(
        ops_entrypoint=SimpleNamespace(remote=lambda *_args, **_kwargs: None)
    )

    monkeypatch.setattr(
        "eclypse.simulation._simulator.ops_handler.ray_backend.get_actor",
        lambda actor_name: actor_names.append(actor_name) or actor,
    )

    remotes = RemoteSimOpsHandler._get_remotes(colocated_placement)

    assert len(remotes) == 2
    assert actor_names == ["edge-cloud/edge-a"]


def test_remote_ops_handler_deploy_start_stop_and_undeploy(
    monkeypatch,
    mapped_placement,
):
    calls: list[tuple[RemoteOps, str]] = []
    node = SimpleNamespace(
        ops_entrypoint=SimpleNamespace(
            remote=lambda operation, service_id, service=None: (
                calls.append((operation, service_id))
                or (operation, service_id, service)
            )
        )
    )

    monkeypatch.setattr(
        RemoteSimOpsHandler,
        "_get_remotes",
        staticmethod(
            lambda placement: [
                (node, service) for service in placement.application.services.values()
            ]
        ),
    )
    monkeypatch.setattr(
        "eclypse.simulation._simulator.ops_handler.ray_backend.get",
        lambda ops: [
            RemoteOpResult(
                code=ResponseCode.OK,
                operation=operation,
                node_id="edge-a",
                service_id=service_id,
                service=service if operation is RemoteOps.UNDEPLOY else None,
            )
            for operation, service_id, service in ops
        ],
    )

    RemoteSimOpsHandler.deploy(mapped_placement)
    RemoteSimOpsHandler.start(mapped_placement)
    RemoteSimOpsHandler.stop(mapped_placement)
    RemoteSimOpsHandler.undeploy(mapped_placement)

    assert mapped_placement.deployed is False
    assert calls == [
        (RemoteOps.DEPLOY, "gateway"),
        (RemoteOps.DEPLOY, "worker"),
        (RemoteOps.START, "gateway"),
        (RemoteOps.START, "worker"),
        (RemoteOps.STOP, "gateway"),
        (RemoteOps.STOP, "worker"),
        (RemoteOps.UNDEPLOY, "gateway"),
        (RemoteOps.UNDEPLOY, "worker"),
    ]


def test_local_simulator_start_stop_trigger_and_properties(
    monkeypatch,
    sample_infrastructure,
    sample_application,
    simulation_config,
    static_strategy,
):
    scheduled: list[tuple[str, object]] = []
    simulator = Simulator(sample_infrastructure, simulation_config)

    monkeypatch.setattr(
        simulator,
        "thread",
        SimpleNamespace(start=lambda: scheduled.append(("thread", None))),
    )
    monkeypatch.setattr(
        "eclypse.simulation._simulator.local.asyncio.run_coroutine_threadsafe",
        lambda coro, loop: scheduled.append(("coroutine", loop)) or coro.close(),
    )

    assert simulator.status is SimulationState.IDLE

    simulator.start()
    simulator.register(sample_application, static_strategy)
    simulator.trigger("stop")
    simulator.stop()

    assert simulator.status is SimulationState.RUNNING
    assert simulator._stop_requested is True
    assert simulator._events["stop"].trigger_bucket._manual_activation == 1
    assert sample_application.id in simulator.applications
    assert simulator.infrastructure is sample_infrastructure
    assert simulator.placement_view is simulator._manager.placement_view
    assert scheduled[0] == ("thread", None)
    assert scheduled[1][0] == "coroutine"


def test_local_simulator_requires_runtime_inputs_and_delegates_helpers(
    monkeypatch,
    sample_infrastructure,
    sample_application,
    simulation_config,
    static_strategy,
):
    original_events = simulation_config.events
    original_path = simulation_config.path
    original_reporters = simulation_config.reporters

    simulation_config.events = None
    with pytest.raises(RuntimeError, match="events must be resolved"):
        Simulator(sample_infrastructure, simulation_config)

    simulation_config.events = original_events
    simulation_config.path = None
    with pytest.raises(RuntimeError, match="path must be resolved"):
        Simulator(sample_infrastructure, simulation_config)

    simulation_config.path = original_path
    simulation_config.reporters = None
    with pytest.raises(RuntimeError, match="reporters must be resolved"):
        Simulator(sample_infrastructure, simulation_config)

    simulation_config.reporters = original_reporters
    simulator = Simulator(sample_infrastructure, simulation_config)
    simulator.register(sample_application, static_strategy)

    scheduled: list[str] = []
    monkeypatch.setattr(
        "eclypse.simulation._simulator.local.asyncio.run_coroutine_threadsafe",
        lambda coro, loop: scheduled.append("scheduled") or coro.close(),
    )

    simulator.stop()
    simulator._status = SimulationState.RUNNING
    simulator._stop_requested = True
    simulator.stop()

    monkeypatch.setattr(simulator._manager, "audit", lambda: scheduled.append("audit"))
    monkeypatch.setattr(simulator._manager, "enact", lambda: scheduled.append("enact"))
    simulator.audit()
    simulator.enact()

    loop_calls: list[object] = []

    class FakeLoop:
        def run_until_complete(self, coro):
            loop_calls.append("run")
            coro.close()

        def close(self):
            loop_calls.append("close")

    fake_loop = FakeLoop()
    fake_simulator = SimpleNamespace(
        _event_loop=fake_loop,
        run=lambda: asyncio.sleep(0),
    )
    monkeypatch.setattr(
        "eclypse.simulation._simulator.local.asyncio.set_event_loop",
        lambda loop: loop_calls.append(("set", loop)),
    )

    _run_loop(fake_simulator)

    assert scheduled == ["audit", "enact"]
    assert sample_application.id in simulator.applications
    assert simulator.placements[sample_application.id].mapping == {}
    assert loop_calls == [("set", fake_loop), "run", "close"]


@pytest.mark.asyncio
async def test_local_simulator_enqueue_event_schedules_post_events(
    sample_infrastructure,
    simulation_config,
):
    simulator = Simulator(sample_infrastructure, simulation_config)
    driving_event = SimpleNamespace(
        name="drive",
        type=None,
        is_post_event=False,
        _trigger=lambda trigger_event=None: False,
    )
    stop_event = SimpleNamespace(
        name="stop",
        type=None,
        is_post_event=False,
        _trigger=lambda trigger_event=None: False,
    )
    metric_event = SimpleNamespace(
        name="metric",
        type="service",
        is_post_event=True,
        _trigger=lambda trigger_event=None: trigger_event.name == "drive",
    )
    simulator._events = {
        "drive": driving_event,
        "stop": stop_event,
        "metric": metric_event,
    }
    simulator._ordered_events = (driving_event, metric_event, stop_event)

    await simulator.enqueue_event("drive")

    assert await simulator._events_queue.get() == {
        "event_name": "drive",
        "triggered_by": None,
    }
    assert await simulator._events_queue.get() == {
        "event_name": "metric",
        "triggered_by": "drive",
    }

    await simulator.enqueue_event("stop")

    assert simulator.status is SimulationState.STOPPING
