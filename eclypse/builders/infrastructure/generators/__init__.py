"""Module for the infrastructure builders.
It has the following builders:

- hierarchical: A hierarchical infrastructure made of nodes partitioned into groups.
- star: A star infrastructure with clients connected to a central node.
- random: A random infrastructure with nodes connected with a given probability.
"""

from .hierarchical import hierarchical
from .fat_tree import fat_tree
from .random import random
from .star import star

__all__ = [
    "hierarchical",
    "fat_tree",
    "random",
    "star",
]
