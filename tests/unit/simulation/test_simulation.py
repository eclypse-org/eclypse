from __future__ import annotations

from types import SimpleNamespace

import pytest

from eclypse.simulation.simulation import (
    Simulation,
    _local_remote_event_call,
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


def test_simulation_wait_handles_single_keyboard_interrupt(
    monkeypatch,
    sample_infrastructure,
    simulation_config,
):
    simulation = Simulation(sample_infrastructure, simulation_config)
    stop_calls: list[bool] = []

    class InterruptibleSimulator:
        def __init__(self):
            self.calls = 0

        def wait(self, timeout=None):
            del timeout
            self.calls += 1
            if self.calls == 1:
                raise KeyboardInterrupt
            return None

    monkeypatch.setattr(simulation, "simulator", InterruptibleSimulator())
    monkeypatch.setattr(
        simulation, "stop", lambda blocking=False: stop_calls.append(blocking)
    )

    simulation.wait()

    assert stop_calls == [False]


def test_simulation_wait_reraises_second_keyboard_interrupt(
    monkeypatch,
    sample_infrastructure,
    simulation_config,
):
    simulation = Simulation(sample_infrastructure, simulation_config)
    stop_calls: list[bool] = []

    class AlwaysInterruptedSimulator:
        def wait(self, timeout=None):
            del timeout
            raise KeyboardInterrupt

    monkeypatch.setattr(simulation, "simulator", AlwaysInterruptedSimulator())
    monkeypatch.setattr(
        simulation, "stop", lambda blocking=False: stop_calls.append(blocking)
    )

    with pytest.raises(KeyboardInterrupt):
        simulation.wait()

    assert stop_calls == [False]


def test_simulation_start_without_path_and_blocking_stop(
    monkeypatch,
    sample_infrastructure,
    simulation_config,
):
    simulation = Simulation(sample_infrastructure, simulation_config)
    calls: list[object] = []
    simulation._sim_config.path = None

    monkeypatch.setattr(
        "eclypse.simulation.simulation._local_remote_event_call",
        lambda sim, remote, fn, *args, **kwargs: calls.append((fn, args, kwargs)),
    )
    monkeypatch.setattr(
        simulation, "wait", lambda timeout=None: calls.append(("wait", timeout))
    )

    simulation.start()
    simulation.stop()

    assert simulation.status is simulation.simulator.status
    assert calls == [
        ("start", (), {}),
        ("stop", (), {}),
        ("wait", None),
    ]


def test_simulation_remote_paths_and_report_cache(
    monkeypatch,
    sample_infrastructure,
    sample_application,
    simulation_config,
    static_strategy,
):
    ray_calls: list[object] = []
    report_calls: list[tuple[object, object, object]] = []

    class RemoteActor:
        def __init__(self):
            self.register = SimpleNamespace(
                remote=lambda app, strategy: ("register", app.id, strategy)
            )
            self.wait = SimpleNamespace(remote=lambda timeout=None: ("wait", timeout))
            self.get_status = SimpleNamespace(remote=lambda: "REMOTE-STATUS")

    remote_actor = RemoteActor()
    remote = SimpleNamespace(
        env_vars=None,
        build=lambda **_kwargs: remote_actor,
    )
    simulation_config.remote = remote
    monkeypatch.setattr(
        "eclypse.simulation.simulation.ray_backend.get",
        lambda value: ray_calls.append(value) or value,
    )
    monkeypatch.setattr(
        "eclypse.simulation.simulation.Report",
        lambda path, backend, fmt: (
            report_calls.append((path, backend, fmt)) or "report"
        ),
    )

    simulation = Simulation(sample_infrastructure, simulation_config)
    simulation.register(sample_application, static_strategy)
    simulation.wait(timeout=2.0)

    assert simulation.status == "REMOTE-STATUS"
    assert simulation.report == "report"
    assert simulation.report == "report"
    assert remote.env_vars == simulation_config.runtime_env()
    assert ("register", sample_application.id, static_strategy) in ray_calls
    assert ("wait", 2.0) in ray_calls
    assert ("wait", None) in ray_calls
    assert report_calls == [
        (
            simulation.path,
            simulation_config.report_backend,
            simulation_config.report_format,
        )
    ]

    with pytest.raises(ValueError, match="All services must have a logic"):
        simulation.register(
            SimpleNamespace(id="plain-app", has_logic=False), static_strategy
        )


def test_simulation_register_prefers_global_strategy_and_requires_one(
    monkeypatch,
    sample_infrastructure,
    sample_application,
    simulation_config,
    static_strategy,
    dummy_logger,
):
    simulation = Simulation(sample_infrastructure, simulation_config)

    with pytest.raises(ValueError, match="Must provide a global placement strategy"):
        simulation.register(sample_application)

    sample_infrastructure.strategy = static_strategy
    monkeypatch.setattr(simulation, "_logger", dummy_logger)
    simulation.register(sample_application, static_strategy)

    assert sample_application.id in simulation.applications
    assert any(level == "warning" for level, _ in dummy_logger.records)
