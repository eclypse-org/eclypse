"""Wrapper package for core utils, constants, and exceptions.

For the complete documentation, refer to :py:mod:`eclypse_core.utils`.
"""

from eclypse_core.utils.constants import (
    MIN_FLOAT,
    MAX_FLOAT,
    FLOAT_EPSILON,
    MIN_BANDWIDTH,
    MAX_BANDWIDTH,
    MIN_LATENCY,
    MAX_LATENCY,
    MIN_AVAILABILITY,
    MAX_AVAILABILITY,
    DEFAULT_SIM_PATH,
)

from eclypse_core.utils.types import CallbackType

__all__ = [
    "MIN_FLOAT",
    "MAX_FLOAT",
    "FLOAT_EPSILON",
    "MIN_BANDWIDTH",
    "MAX_BANDWIDTH",
    "MIN_LATENCY",
    "MAX_LATENCY",
    "MIN_AVAILABILITY",
    "MAX_AVAILABILITY",
    "DEFAULT_SIM_PATH",
    "CallbackType",
]
