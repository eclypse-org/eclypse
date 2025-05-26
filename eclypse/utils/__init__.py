"""Wrapper package for core utils, constants, and exceptions.

For the complete documentation, refer to the :py:mod:`~eclypse_core.utils` core package.
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
    DEFAULT_REPORT_TYPE,
)

from eclypse_core.utils.types import CallbackType, PrimitiveType

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
    "DEFAULT_REPORT_TYPE",
    "CallbackType",
    "PrimitiveType",
]
