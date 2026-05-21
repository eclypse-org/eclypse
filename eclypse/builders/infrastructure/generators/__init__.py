"""Infrastructure generators (e.g. get_star, get_hierarchical, get_small_world).

The package collects topology-first infrastructure builders whose primary role is to
generate reusable graph families. These generators expose structural models such as
stars, random graphs, layered hierarchies, and data-centre or hub-oriented networks
without tying them to a specific application domain.
"""

from .b_cube import get_b_cube
from .fat_tree import get_fat_tree
from .hierarchical import get_hierarchical
from .random import get_random
from .scale_free import get_scale_free
from .small_world import get_small_world
from .star import get_star

__all__ = [
    "get_b_cube",
    "get_fat_tree",
    "get_hierarchical",
    "get_random",
    "get_scale_free",
    "get_small_world",
    "get_star",
]
