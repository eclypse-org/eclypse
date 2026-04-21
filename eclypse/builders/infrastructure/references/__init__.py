"""Infrastructure references (e.g. get_orion_cev, topohub).

The package groups concrete named topologies reconstructed from papers,
datasets, or standards-oriented reference material. It includes both specific
reference builders and dataset-backed loader families, such as the TopoHub
subpackage for SNDlib, CAIDA, Gabriel, backbone, and Topology Zoo references.
"""

from .orion_cev import get_orion_cev
from . import topohub

__all__ = [
    "get_orion_cev",
    "topohub",
]
