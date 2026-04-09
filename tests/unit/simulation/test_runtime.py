from __future__ import annotations

import os

from eclypse.simulation.runtime import (
    apply_runtime_env,
    build_runtime_env,
)
from eclypse.utils.constants import (
    LOG_FILE,
    LOG_LEVEL,
    RND_SEED,
)


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
