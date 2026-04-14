"""Domain and low-level constants shared across ECLYPSE."""

from __future__ import annotations

import sys

# Numeric domains

MIN_FLOAT = 0.0
"""Smallest domain value accepted by numeric assets."""

MAX_FLOAT = 1e9
"""Largest domain value used for bounded numeric defaults."""

FLOAT_EPSILON = sys.float_info.min
"""Smallest positive representable float."""

# Environment

RND_SEED = "ECLYPSE_RND_SEED"
"""Environment variable used to seed deterministic randomness."""

LOG_LEVEL = "ECLYPSE_LOG_LEVEL"
"""Environment variable used to configure the logger level."""

LOG_FILE = "ECLYPSE_LOG_FILE"
"""Environment variable used to configure the log file path."""

# Assets

MIN_BANDWIDTH = MIN_FLOAT
"""Lower bound used by bandwidth assets."""

MAX_BANDWIDTH = MAX_FLOAT
"""Upper bound used by bandwidth assets."""

MIN_LATENCY = MIN_FLOAT
"""Lower bound used by latency assets."""

MAX_LATENCY = MAX_FLOAT
"""Upper bound used by latency assets."""

MIN_AVAILABILITY = 0.0
"""Lower bound used by availability assets."""

MAX_AVAILABILITY = 1.0
"""Upper bound used by availability assets."""

# Infrastructure

COST_RECOMPUTATION_THRESHOLD = 0.05
"""Relative threshold above which cached path costs are recomputed."""

# Workflow

START_EVENT = "start"
"""Name of the default simulation start event."""

ENACT_EVENT = "enact"
"""Name of the default simulation enactment event."""

STEP_EVENT = "step"
"""Name of the default simulation step event."""

STOP_EVENT = "stop"
"""Name of the default simulation stop event."""

DRIVING_EVENT = ENACT_EVENT
"""Name of the default driving event used to advance the simulation."""

__all__ = [
    "COST_RECOMPUTATION_THRESHOLD",
    "DRIVING_EVENT",
    "ENACT_EVENT",
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
    "START_EVENT",
    "STEP_EVENT",
    "STOP_EVENT",
]
