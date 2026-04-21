"""Infrastructure patterns (e.g. continuum_tiered, mec_5g, factory_cells).

The package groups parameterised infrastructure blueprints whose structure is
tied to an architectural deployment model rather than to a pure graph family.
These builders encode recognisable system layouts such as cloud-edge continua,
MEC deployments, industrial cells, and vehicular edge backbones.
"""

from .continuum_tiered import continuum_tiered
from .factory_cells import factory_cells
from .industrial_tsn import industrial_tsn
from .mec_5g import mec_5g
from .multi_region_wan import multi_region_wan
from .vehicular_edge import vehicular_edge

__all__ = [
    "continuum_tiered",
    "factory_cells",
    "industrial_tsn",
    "mec_5g",
    "multi_region_wan",
    "vehicular_edge",
]
