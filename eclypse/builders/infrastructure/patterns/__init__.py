"""Infrastructure patterns (e.g. get_continuum_tiered, get_mec_5g).

The package groups parameterised infrastructure blueprints whose structure is
tied to an architectural deployment model rather than to a pure graph family.
These builders encode recognisable system layouts such as cloud-edge continua,
MEC deployments, industrial cells, and vehicular edge backbones.
"""

from .continuum_tiered import get_continuum_tiered
from .factory_cells import get_factory_cells
from .industrial_tsn import get_industrial_tsn
from .mec_5g import get_mec_5g
from .multi_region_wan import get_multi_region_wan
from .vehicular_edge import get_vehicular_edge

__all__ = [
    "get_continuum_tiered",
    "get_factory_cells",
    "get_industrial_tsn",
    "get_mec_5g",
    "get_multi_region_wan",
    "get_vehicular_edge",
]
