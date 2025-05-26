"""Package for the MPI communication interface, based on the Message Passing Interface
(MPI) protocol.

For the complete documentation, refer to the :py:mod:`~eclypse_core.remote.communication.mpi`
core package.
"""

from eclypse_core.remote.communication.mpi import (
    EclypseMPI,
    Response,
    exchange,
)

__all__ = [
    "EclypseMPI",
    "Response",
    "exchange",
]
