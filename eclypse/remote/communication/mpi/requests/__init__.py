"""Package collecting the different types of requests that can be sent to the remote
nodes, using the MPI communication protocol."""

from .multicast import MulticastRequest
from .broadcast import BroadcastRequest
from .unicast import UnicastRequest

__all__ = [
    "BroadcastRequest",
    "MulticastRequest",
    "UnicastRequest",
]
