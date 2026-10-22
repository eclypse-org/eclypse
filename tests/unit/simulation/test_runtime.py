from __future__ import annotations

import os

from eclypse.simulation.config import SimulationConfig
from eclypse.simulation.runtime import (
    apply_runtime_env,
    build_runtime_env,
)
from eclypse.utils.constants import (
    LOG_FILE,
    LOG_LEVEL,
    RND_SEED,
)
from eclypse.utils.defaults import DEFAULT_RAY_RUNTIME_ENV_VARS


def test_build_and_apply_runtime_env(monkeypatch, tmp_path):
    calls: list[str] = []
    # restore the variables set by apply_runtime_env after the test
    for key in (RND_SEED, LOG_LEVEL, LOG_FILE):
        monkeypatch.delenv(key, raising=False)

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


def test_default_ray_runtime_env_disables_ray_uv_runtime():
    assert DEFAULT_RAY_RUNTIME_ENV_VARS["RAY_ENABLE_UV_RUN_RUNTIME_ENV"] == "0"


def test_runtime_env_follows_the_latest_prepared_simulation(
    monkeypatch, tmp_path, list_frame_backend
):
    for key in (RND_SEED, LOG_LEVEL, LOG_FILE):
        monkeypatch.delenv(key, raising=False)
    monkeypatch.setattr("eclypse.simulation.runtime.config_logger", lambda: None)

    SimulationConfig(
        seed=1,
        log_level="DEBUG",
        log_to_file=True,
        path=tmp_path / "first",
        report_backend=list_frame_backend,
    ).prepare_runtime()
    SimulationConfig(
        seed=2,
        log_level="INFO",
        path=tmp_path / "second",
        report_backend=list_frame_backend,
    ).prepare_runtime()

    assert os.environ[RND_SEED] == "2"
    assert os.environ[LOG_LEVEL] == "INFO"
    # the second simulation does not log to file, so the first one's file is unset
    assert LOG_FILE not in os.environ
