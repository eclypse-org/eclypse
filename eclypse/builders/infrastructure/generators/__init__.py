"""Module for the infrastructure builders.
It has the following builders:

- b_cube: A BCube infrastructure with switches and hosts.
- fat_tree: A Fat-Tree infrastructure with switches and hosts.
- hierarchical: A hierarchical infrastructure made of nodes partitioned into groups.
- star: A star infrastructure with clients connected to a central node.
- random: A random infrastructure with nodes connected with a given probability.
"""

from .b_cube import b_cube
from .fat_tree import fat_tree
from .hierarchical import hierarchical
from .random import random
from .star import star

__all__ = [
    "b_cube",
    "fat_tree",
    "hierarchical",
    "random",
    "star",
]
