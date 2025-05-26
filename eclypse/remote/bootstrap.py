"""Package for managing configuration of remote nodes.

For the complete documentation, refer to the :py:mod:`~eclypse_core.remote.bootstrap`
core package.
"""

from eclypse_core.remote.bootstrap import (
    RayOptionsFactory,
    RemoteBootstrap,
)

__all__ = [
    "RemoteBootstrap",
    "RayOptionsFactory",
]
