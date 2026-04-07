from __future__ import annotations

import asyncio
from types import SimpleNamespace

import pytest

from eclypse.report.reporter import Reporter
from eclypse.simulation._simulator.reporter import SimulationReporter
from eclypse.simulation.simulation import Simulation


class RecordingReporter(Reporter):
    instances: list["RecordingReporter"] = []

    def __init__(self, report_path):
        super().__init__(report_path)
        self.started = False
        self.closed = False
        self.writes: list[tuple[str, list[list[object]]]] = []
        self.__class__.instances.append(self)

    async def init(self):
        await super().init()
        self.started = True

    async def close(self):
        self.closed = True

    async def write(self, callback_type: str, data):
        self.writes.append((callback_type, list(data)))

    def report(self, event_name: str, event_idx: int, callback):
        del event_name, event_idx
        yield from self.callback_rows(callback)


@pytest.mark.asyncio
async def test_simulation_reporter_buffers_flushes_and_closes(tmp_path):
    RecordingReporter.instances.clear()
    reporter = SimulationReporter(tmp_path, {"csv": RecordingReporter}, chunk_size=2)
    callback = SimpleNamespace(
        is_metric=True,
        data=(("shop", "gateway", 3.5),),
        type="service",
        name="latency_metric",
        report_types=["csv"],
    )

    await reporter.start(asyncio.get_running_loop())
    await reporter.report("step", 1, callback)
    await reporter.report("step", 2, callback)
    await reporter.stop()

    recording = RecordingReporter.instances[0]

    assert recording.started is True
    assert recording.closed is True
    assert recording.writes == [
        ("service", [["shop", "gateway", 3.5], ["shop", "gateway", 3.5]])
    ]


@pytest.mark.asyncio
async def test_simulation_reporter_handles_dynamic_reporters_and_filtered_callbacks(
    monkeypatch,
    tmp_path,
    dummy_logger,
):
    class NullReporter(RecordingReporter):
        def report(self, event_name: str, event_idx: int, callback):
            del event_name, event_idx, callback
            return None

    RecordingReporter.instances.clear()
    reporter = SimulationReporter(tmp_path, {"csv": RecordingReporter}, chunk_size=4)
    monkeypatch.setattr("eclypse.simulation._simulator.reporter.logger", dummy_logger)

    reporter.add_reporter("json", RecordingReporter)
    reporter.add_reporter("null", NullReporter)
    await reporter.start(asyncio.get_running_loop())
    await reporter.start(asyncio.get_running_loop())

    await reporter.report(
        "step",
        1,
        SimpleNamespace(type=None, report_types=["csv"]),
    )
    await reporter.report(
        "step",
        2,
        SimpleNamespace(type="service", report_types=["missing", "null"]),
    )
    await reporter.stop()

    assert set(reporter.reporters) == {"csv", "json", "null"}
    assert reporter.queues["null"] == {}
    assert any(
        "No reporter registered" in args[0]
        for level, args in dummy_logger.records
        if level == "warning"
    )


@pytest.mark.asyncio
async def test_simulation_reporter_handles_writer_failures_and_cancellation(
    monkeypatch,
    tmp_path,
    dummy_logger,
):
    class ImmediateFailReporter(RecordingReporter):
        async def write(self, callback_type: str, data):
            del callback_type, data
            raise RuntimeError("write boom")

    class FinalFlushFailReporter(RecordingReporter):
        async def write(self, callback_type: str, data):
            del callback_type, data
            raise RuntimeError("flush boom")

    RecordingReporter.instances.clear()
    reporter = SimulationReporter(
        tmp_path,
        {
            "write": ImmediateFailReporter,
            "flush": FinalFlushFailReporter,
            "cancel": RecordingReporter,
        },
        chunk_size=2,
    )
    monkeypatch.setattr("eclypse.simulation._simulator.reporter.logger", dummy_logger)
    await reporter.start(asyncio.get_running_loop())

    write_queue = reporter._ensure_queue("write", "service")
    flush_queue = reporter._ensure_queue("flush", "service")
    cancel_queue = reporter._ensure_queue("cancel", "service")
    assert cancel_queue is reporter.queues["cancel"]["service"]

    await write_queue.put([["shop"], ["worker"]])
    await flush_queue.put([["gateway"]])
    await write_queue.join()
    await flush_queue.join()

    cancel_task = reporter.writer_tasks["cancel"]["service"]
    cancel_task.cancel()
    await asyncio.gather(cancel_task, return_exceptions=True)

    await reporter.stop()

    error_messages = [
        args[0] for level, args in dummy_logger.records if level == "error"
    ]
    trace_messages = [
        args[0] for level, args in dummy_logger.records if level == "trace"
    ]
    assert any("write boom" in message for message in error_messages)
    assert any("flush boom" in message for message in error_messages)
    assert any("cancelled" in message for message in trace_messages)


def test_simulation_reporter_requires_started_loop_and_skips_duplicates(
    monkeypatch,
    tmp_path,
    dummy_logger,
):
    reporter = SimulationReporter(tmp_path, {"csv": RecordingReporter}, chunk_size=1)
    monkeypatch.setattr("eclypse.simulation._simulator.reporter.logger", dummy_logger)

    reporter.add_reporter("csv", RecordingReporter)

    with pytest.raises(RuntimeError, match="Call start\\(\\) first"):
        reporter._ensure_queue("csv", "service")

    assert any(level == "warning" for level, _ in dummy_logger.records)


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
