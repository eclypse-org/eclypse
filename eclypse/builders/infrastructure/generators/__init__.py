"""Infrastructure generators (e.g. star, hierarchical, small_world).

The package collects topology-first infrastructure builders whose primary role
is to generate reusable graph families. These generators expose structural
models such as stars, random graphs, layered hierarchies, and data-centre or
hub-oriented networks without tying them to a specific application domain.
"""

from .b_cube import b_cube
from .fat_tree import fat_tree
from .hierarchical import hierarchical
from .random import random
from .scale_free import scale_free
from .small_world import small_world
from .star import star

__all__ = [
    "b_cube",
    "fat_tree",
    "hierarchical",
    "random",
    "scale_free",
    "small_world",
    "star",
]
