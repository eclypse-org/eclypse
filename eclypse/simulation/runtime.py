"""Runtime environment helpers for simulations."""

from __future__ import annotations

import os
from typing import (
    TYPE_CHECKING,
    Dict,
)

from eclypse.utils._logging import config_logger
from eclypse.utils.constants import (
    LOG_FILE,
    LOG_LEVEL,
    RND_SEED,
)

if TYPE_CHECKING:
    from pathlib import Path

RUNTIME_ENV_DEFAULTS: Dict[str, str] = {
    "RAY_DEDUP_LOGS": "0",
    "RAY_COLOR_PREFIX": "1",
}


def build_runtime_env(
    seed: int,
    log_level: str,
    path: Path,
    log_to_file: bool,
) -> Dict[str, str]:
    """Build the environment variables required by a simulation runtime."""
    env_vars = {
        **RUNTIME_ENV_DEFAULTS,
        RND_SEED: str(seed),
        LOG_LEVEL: log_level,
    }
    if log_to_file:
        env_vars[LOG_FILE] = str(path / "simulation.log")
    return env_vars


def apply_runtime_env(env_vars: Dict[str, str]):
    """Apply runtime environment variables and refresh logging configuration."""
    os.environ.update(env_vars)
    config_logger()
