"""Package for managing configuration of remote nodes.

For the complete documentation, refer to :py:mod:`eclypse_core.remote.bootstrap`.
"""

from eclypse_core.remote.bootstrap import (
    RayOptionsFactory,
    RemoteBootstrap,
)

__all__ = [
    "RemoteBootstrap",
    "RayOptionsFactory",
]
