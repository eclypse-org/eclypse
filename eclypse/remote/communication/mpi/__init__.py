"""Package for the MPI communication interface.

Based on the `Message Passing Interface (MPI) protocol
<https://en.wikipedia.org/wiki/Message_Passing_Interface>`_.
"""

from .message import Message
from .response import Response
from .interface import EclypseMPI, exchange

__all__ = [
    "EclypseMPI",
    "Message",
    "Response",
    "exchange",
]
