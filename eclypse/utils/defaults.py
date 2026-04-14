"""Configurable defaults and well-known output names used across ECLYPSE."""

from __future__ import annotations

from pathlib import Path

from eclypse.utils.constants import MAX_FLOAT

# Reporting

DEFAULT_REPORT_TYPE = "csv"
"""Default on-disk format used to write simulation reports."""

DEFAULT_REPORT_BACKEND = "pandas"
"""Default backend used to load report frames."""

DEFAULT_REPORT_CHUNK_SIZE = 100
"""Default number of rows buffered before flushing report batches."""

DEFAULT_STEP_QUEUE_SIZE = 1024
"""Default maximum number of stored service step results."""

DEFAULT_EDGE_LATENCY = 1.0
"""Default latency used when a link does not define one explicitly."""

DEFAULT_REPORT_RANGE = (0, int(MAX_FLOAT))
"""Default inclusive event range used by report queries."""

DEFAULT_REPORT_STEP = 1
"""Default sampling step used by report queries."""

# Simulation

SIMULATION_CONFIG_FILENAME = "config.json"
"""Filename used to persist the simulation configuration."""

SIMULATION_LOG_FILENAME = "simulation.log"
"""Filename used for simulation runtime logs."""

# Reporters

CSV_REPORT_DIR = "csv"
"""Directory name used by the CSV reporter."""

GML_REPORT_DIR = "gml"
"""Directory name used by the GML reporter."""

JSON_REPORT_DIR = "json"
"""Directory name used by the JSON reporter."""

PARQUET_REPORT_DIR = "parquet"
"""Directory name used by the Parquet reporter."""

TENSORBOARD_REPORT_DIR = "tensorboard"
"""Directory name used by the TensorBoard reporter."""

DEFAULT_RAY_RUNTIME_ENV_VARS: dict[str, str] = {
    "RAY_DEDUP_LOGS": "0",
    "RAY_COLOR_PREFIX": "1",
}
"""Default Ray environment variables applied to simulation runtimes."""

# Paths


def get_default_sim_path() -> Path:
    """Return the default path where simulation outputs are stored."""
    return Path.home() / "eclypse-sim"


__all__ = [
    "CSV_REPORT_DIR",
    "DEFAULT_EDGE_LATENCY",
    "DEFAULT_RAY_RUNTIME_ENV_VARS",
    "DEFAULT_REPORT_BACKEND",
    "DEFAULT_REPORT_CHUNK_SIZE",
    "DEFAULT_REPORT_RANGE",
    "DEFAULT_REPORT_STEP",
    "DEFAULT_REPORT_TYPE",
    "DEFAULT_STEP_QUEUE_SIZE",
    "GML_REPORT_DIR",
    "JSON_REPORT_DIR",
    "PARQUET_REPORT_DIR",
    "SIMULATION_CONFIG_FILENAME",
    "SIMULATION_LOG_FILENAME",
    "TENSORBOARD_REPORT_DIR",
    "get_default_sim_path",
]
