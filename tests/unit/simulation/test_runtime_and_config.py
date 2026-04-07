from __future__ import annotations

import os
from pathlib import Path

import pytest

from eclypse.remote.bootstrap import RemoteBootstrap
from eclypse.simulation.config import (
    SimulationConfig,
    _catch_duplicates,
    _require_module,
)
from eclypse.simulation.runtime import (
    apply_runtime_env,
    build_runtime_env,
)
from eclypse.utils.constants import (
    DRIVING_EVENT,
    LOG_FILE,
    LOG_LEVEL,
    RND_SEED,
    STOP_EVENT,
)
from eclypse.workflow.event import EclypseEvent
from eclypse.workflow.event.role import EventRole


class ConfigEvent(EclypseEvent):
    def __init__(self, name: str, **kwargs):
        super().__init__(name=name, **kwargs)

    def __call__(self, *_args, **_kwargs):
        return {}


def test_build_and_apply_runtime_env(monkeypatch, tmp_path):
    calls: list[str] = []

    monkeypatch.setattr(
        "eclypse.simulation.runtime.config_logger", lambda: calls.append("configured")
    )
    env = build_runtime_env(
        seed=17,
        log_level="DEBUG",
        path=tmp_path,
        log_to_file=True,
    )

    apply_runtime_env(env)

    assert os.environ[RND_SEED] == "17"
    assert os.environ[LOG_LEVEL] == "DEBUG"
    assert os.environ[LOG_FILE].endswith("simulation.log")
    assert calls == ["configured"]


def test_simulation_config_normalises_and_serialises(list_frame_backend, tmp_path):
    config = SimulationConfig(
        path=tmp_path / "run",
        report_backend=list_frame_backend,
        step_every_ms="auto",
        timeout=1.5,
        max_steps=3,
        include_default_metrics=True,
    )

    assert config.step_every_ms == 0.0
    assert config.path == tmp_path / "run"
    assert config.runtime_env()[RND_SEED] == str(config.seed)
    assert "csv" in config.reporters
    assert all(not event.remote for event in config.events)
    assert config.to_dict()["max_steps"] == 3


def test_simulation_config_rejects_invalid_step_and_duplicate_keys(list_frame_backend):
    with pytest.raises(ValueError, match="step_every_ms"):
        SimulationConfig(step_every_ms="sometimes", report_backend=list_frame_backend)

    with pytest.raises(ValueError, match="Duplicated event found"):
        _catch_duplicates([1, 1], lambda value: value, "event")


def test_require_module_surfaces_install_hint():
    with pytest.raises(ImportError, match="pip install eclypse\\[remote\\]"):
        _require_module("module_that_does_not_exist", extras_name="remote")


def test_simulation_config_helper_methods_cover_optional_paths(monkeypatch, tmp_path):
    require_calls: list[tuple[str, str | None]] = []

    monkeypatch.setattr(
        "eclypse.simulation.config._require_module",
        lambda module, extras_name=None: require_calls.append((module, extras_name)),
    )
    monkeypatch.setattr(
        "eclypse.simulation.config.strftime", lambda _fmt: "20260407_120000"
    )

    existing_path = tmp_path / "run"
    existing_path.mkdir()

    assert SimulationConfig._resolve_step_every_ms(2) == 2
    assert SimulationConfig._resolve_step_every_ms(None) is None
    assert SimulationConfig._resolve_path(existing_path) == Path(
        f"{existing_path}-20260407_120000"
    )

    bootstrap = RemoteBootstrap()
    assert SimulationConfig._resolve_remote(bootstrap) is bootstrap

    config = object.__new__(SimulationConfig)
    config.reporters = None

    with pytest.raises(RuntimeError, match="Reporters must be resolved"):
        config._ensure_optional_dependencies()

    config.reporters = {"tensorboard": object, "parquet": object}
    config.remote = bootstrap
    config.report_backend = "pandas"
    config._ensure_optional_dependencies()

    assert require_calls == [
        ("tensorboardX", "tboard"),
        ("polars", None),
        ("ray", "remote"),
        ("pandas", None),
    ]

    require_calls.clear()
    config.report_backend = "polars_lazy"
    config._ensure_optional_dependencies()

    assert require_calls == [
        ("tensorboardX", "tboard"),
        ("polars", None),
        ("ray", "remote"),
        ("polars", None),
    ]


def test_simulation_config_validation_and_serialisation_guards(
    monkeypatch, dummy_logger
):
    monkeypatch.setattr("eclypse.simulation.config.logger", dummy_logger)

    config = object.__new__(SimulationConfig)
    config.events = None

    with pytest.raises(RuntimeError, match="Events must be resolved"):
        config._validate()

    config.events = [ConfigEvent(DRIVING_EVENT)]
    config.remote = None
    config.step_every_ms = None
    config.max_steps = None
    config.timeout = None

    with pytest.raises(ValueError, match="A 'stop' event must be defined"):
        config._validate()

    config.events = [ConfigEvent(STOP_EVENT)]

    with pytest.raises(ValueError, match="An 'enact' event must be defined"):
        config._validate()

    remote_callback = ConfigEvent("remote_callback", remote=True)
    stop_event = ConfigEvent(STOP_EVENT)
    enact_event = ConfigEvent(DRIVING_EVENT)
    config.events = [remote_callback, stop_event, enact_event]
    config._validate()

    assert [event.name for event in config.events] == [STOP_EVENT, DRIVING_EVENT]
    assert enact_event.trigger_bucket.condition == "all"
    assert stop_event.trigger_bucket.condition == "all"
    assert [args[0] for level, args in dummy_logger.records if level == "warning"] == [
        "Manual simulation required!",
        "Use 'step()' to advance the simulation, and 'stop()' to interrupt it.",
    ]

    config.events = None
    assert config.callbacks == []

    config.reporters = None

    with pytest.raises(RuntimeError, match="fully initialized"):
        config.to_dict()

    remote_metric = ConfigEvent("remote_metric", remote=True, role=EventRole.METRIC)
    stop_event = ConfigEvent(STOP_EVENT)
    enact_event = ConfigEvent(DRIVING_EVENT)
    config.events = [remote_metric, stop_event, enact_event]
    config.remote = RemoteBootstrap()
    config._validate()

    assert config.callbacks == [remote_metric]


def test_prepare_runtime_is_idempotent(monkeypatch, tmp_path, list_frame_backend):
    applied_envs: list[dict[str, str]] = []

    monkeypatch.setattr(
        "eclypse.simulation.config.apply_runtime_env",
        lambda runtime_env: applied_envs.append(runtime_env),
    )

    config = SimulationConfig(
        path=tmp_path / "prepared",
        report_backend=list_frame_backend,
    )

    config.prepare_runtime()
    config.prepare_runtime()

    assert len(applied_envs) == 1
