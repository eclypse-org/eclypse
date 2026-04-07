"""Runtime environment helpers for simulations."""

from __future__ import annotations

import os
from typing import (
    TYPE_CHECKING,
)

from eclypse.utils._logging import config_logger
from eclypse.utils.constants import (
    LOG_FILE,
    LOG_LEVEL,
    RND_SEED,
)
from eclypse.utils.defaults import (
    DEFAULT_RAY_RUNTIME_ENV_VARS,
    SIMULATION_LOG_FILENAME,
)

if TYPE_CHECKING:
    from pathlib import Path


def build_runtime_env(
    seed: int,
    log_level: str,
    path: Path,
    log_to_file: bool,
) -> dict[str, str]:
    """Build the environment variables required by a simulation runtime."""
    env_vars = {
        **DEFAULT_RAY_RUNTIME_ENV_VARS,
        RND_SEED: str(seed),
        LOG_LEVEL: log_level,
    }
    if log_to_file:
        env_vars[LOG_FILE] = str(path / SIMULATION_LOG_FILENAME)
    return env_vars


def apply_runtime_env(env_vars: dict[str, str]):
    """Apply runtime environment variables and refresh logging configuration."""
    os.environ.update(env_vars)
    config_logger()
