"""Package for simulation configuration and engine.

The engine documentation can be found at :py:class:`eclypse_core.simulation.simulation.Simulation`.
"""

from eclypse_core.simulation import Simulation
from .config import SimulationConfig

__all__ = [
    "Simulation",
    "SimulationConfig",
]
