"""Package collecting placement strategies that can be used to place services of an
application on infrastructure nodes."""

from .strategy import PlacementStrategy
from .round_robin import RoundRobinStrategy
from .random import RandomStrategy
from .static import StaticStrategy
from .first_fit import FirstFitStrategy
from .best_fit import BestFitStrategy

__all__ = [
    "PlacementStrategy",
    "RoundRobinStrategy",
    "RandomStrategy",
    "StaticStrategy",
    "FirstFitStrategy",
    "BestFitStrategy",
]
