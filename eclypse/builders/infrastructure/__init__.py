"""Infrastructure builders (e.g. hierarchical, mec_5g, get_orion_cev).

The package groups the off-the-shelf infrastructure builders provided by
ECLYPSE. It combines generic topology generators, architecture-shaped
deployment patterns, and named reference topologies derived from literature or
datasets, while re-exporting them from a single public entrypoint.
"""

from . import (
    generators,
    patterns,
    references,
)
from .generators import (
    b_cube,
    fat_tree,
    hierarchical,
    random,
    scale_free,
    small_world,
    star,
)
from .patterns import (
    continuum_tiered,
    factory_cells,
    industrial_tsn,
    mec_5g,
    multi_region_wan,
    vehicular_edge,
)
from .references import get_orion_cev
from .references.topohub import (
    get_backbone,
    get_caida,
    get_gabriel,
    get_sndlib,
    get_topohub,
    get_topology_zoo,
)

__all__ = [
    "b_cube",
    "continuum_tiered",
    "factory_cells",
    "fat_tree",
    "generators",
    "get_backbone",
    "get_caida",
    "get_gabriel",
    "get_orion_cev",
    "get_sndlib",
    "get_topohub",
    "get_topology_zoo",
    "hierarchical",
    "industrial_tsn",
    "mec_5g",
    "multi_region_wan",
    "patterns",
    "random",
    "references",
    "scale_free",
    "small_world",
    "star",
    "vehicular_edge",
]
