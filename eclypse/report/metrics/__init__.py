"""Package for managing reportable metrics in an ECLYPSE simulation.

It provides a set of decorators to define metrics at different levels of the simulation.
"""

from .metric import (
    simulation,
    application,
    infrastructure,
    service,
    interaction,
    node,
    link,
)

__all__ = [
    # DECORATORS
    "simulation",
    "application",
    "infrastructure",
    "service",
    "interaction",
    "node",
    "link",
]
