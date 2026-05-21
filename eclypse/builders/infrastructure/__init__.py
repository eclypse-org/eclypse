"""Infrastructure builders (e.g. get_hierarchical, get_mec_5g, get_orion_cev).

The package groups the off-the-shelf infrastructure builders provided by ECLYPSE. It
combines generic topology generators, architecture-shaped deployment patterns, and named
reference topologies derived from literature or datasets, while re-exporting them from a
single public entrypoint.
"""

from . import (
    generators,
    patterns,
    references,
)
from .generators import (
    get_b_cube,
    get_fat_tree,
    get_hierarchical,
    get_random,
    get_scale_free,
    get_small_world,
    get_star,
)
from .patterns import (
    get_continuum_tiered,
    get_factory_cells,
    get_industrial_tsn,
    get_mec_5g,
    get_multi_region_wan,
    get_vehicular_edge,
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
    "generators",
    "get_b_cube",
    "get_backbone",
    "get_caida",
    "get_continuum_tiered",
    "get_factory_cells",
    "get_fat_tree",
    "get_gabriel",
    "get_hierarchical",
    "get_industrial_tsn",
    "get_mec_5g",
    "get_multi_region_wan",
    "get_orion_cev",
    "get_random",
    "get_scale_free",
    "get_small_world",
    "get_sndlib",
    "get_star",
    "get_topohub",
    "get_topology_zoo",
    "get_vehicular_edge",
    "patterns",
    "references",
]
