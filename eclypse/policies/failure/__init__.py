"""Built-in failure-oriented update policies."""

from __future__ import annotations

from .availability_flap import availability_flap
from .brownout import brownout
from .correlated_failure import correlated_failure
from .edge_availability_flap import edge_availability_flap
from .kill_edges import kill_edges
from .kill_nodes import kill_nodes
from .latency_spike import latency_spike
from .network_partition import network_partition
from .resource_exhaustion import resource_exhaustion
from .revive_edges import revive_edges
from .revive_nodes import revive_nodes

__all__ = [
    "availability_flap",
    "brownout",
    "correlated_failure",
    "edge_availability_flap",
    "kill_edges",
    "kill_nodes",
    "latency_spike",
    "network_partition",
    "resource_exhaustion",
    "revive_edges",
    "revive_nodes",
]
