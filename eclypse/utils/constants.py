"""Module containing constants used throughout the ECLYPSE package.

Attributes:
    MIN_FLOAT (float): Minimum float value. Default is ``0.0``
    MAX_FLOAT (float): Maximum float value. Default is ``1e9``
    FLOAT_EPSILON (float): Smallest positive float (machine epsilon).
        Default is ``sys.float_info.min``

    MIN_BANDWIDTH (float): Minimum bandwidth value. Default is ``0.0``
    MAX_BANDWIDTH (float): Maximum bandwidth value. Default is ``1e9``

    MIN_LATENCY (float): Minimum latency value. Default is ``0.0``
    MAX_LATENCY (float): Maximum latency value. Default is ``1e9``

    MIN_AVAILABILITY (float): Minimum availability value. Default is ``0.0``
    MAX_AVAILABILITY (float): Maximum availability value. Default is ``1.0``

    DEFAULT_SIM_PATH (Path): Default path to the simulation folder.
        Default is ``~/eclypse-sim``

    DEFAULT_REPORT_TYPE (str): Default report type used in simulations.
        Default is ``csv``

    DRIVING_EVENT (str): Name of the event used to drive the simulation.
        Default is ``enact``

    RND_SEED (str): Environment variable key to configure the random seed.
        Value is ``ECLYPSE_RND_SEED``
    LOG_LEVEL (str): Environment variable key to configure the logging level.
        Value is ``ECLYPSE_LOG_LEVEL``
    LOG_FILE (str): Environment variable key to configure the log file path.
        Value is ``ECLYPSE_LOG_FILE``
"""

from eclypse_core.utils.constants import (
    DEFAULT_REPORT_TYPE,
    DEFAULT_SIM_PATH,
    DRIVING_EVENT,
    FLOAT_EPSILON,
    LOG_FILE,
    LOG_LEVEL,
    MAX_AVAILABILITY,
    MAX_BANDWIDTH,
    MAX_FLOAT,
    MAX_LATENCY,
    MIN_AVAILABILITY,
    MIN_BANDWIDTH,
    MIN_FLOAT,
    MIN_LATENCY,
    RND_SEED,
)

__all__ = [
    "DEFAULT_REPORT_TYPE",
    "DEFAULT_SIM_PATH",
    "DRIVING_EVENT",
    "FLOAT_EPSILON",
    "LOG_FILE",
    "LOG_LEVEL",
    "MAX_AVAILABILITY",
    "MAX_BANDWIDTH",
    "MAX_FLOAT",
    "MAX_LATENCY",
    "MIN_AVAILABILITY",
    "MIN_BANDWIDTH",
    "MIN_FLOAT",
    "MIN_LATENCY",
    "RND_SEED",
]
