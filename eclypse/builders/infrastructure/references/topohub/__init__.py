"""TopoHub references (e.g. get_topohub, get_sndlib, get_topology_zoo).

The package groups dataset-backed infrastructure references loaded through the
``topohub`` Python wrapper. It includes a generic ``get_topohub`` entrypoint
for arbitrary TopoHub paths together with family-specific helpers for SNDlib,
the Internet Topology Zoo, CAIDA, synthetic backbones, and Gabriel graphs.
"""

from ._helpers import get_topohub
from .backbone import get_backbone
from .caida import get_caida
from .gabriel import get_gabriel
from .sndlib import get_sndlib
from .topology_zoo import get_topology_zoo

__all__ = [
    "get_backbone",
    "get_caida",
    "get_gabriel",
    "get_sndlib",
    "get_topohub",
    "get_topology_zoo",
]
