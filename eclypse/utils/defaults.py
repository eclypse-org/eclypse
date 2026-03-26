"""Module containing configurable default values used across ECLYPSE."""

from __future__ import annotations

from pathlib import Path

DEFAULT_REPORT_TYPE = "csv"
DEFAULT_REPORT_BACKEND = "pandas"


def get_default_sim_path() -> Path:
    """Return the default path where simulation outputs are stored."""
    return Path.home() / "eclypse-sim"


__all__ = [
    "DEFAULT_REPORT_BACKEND",
    "DEFAULT_REPORT_TYPE",
    "get_default_sim_path",
]
