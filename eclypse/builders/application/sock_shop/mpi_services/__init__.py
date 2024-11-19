"""MPI implementation for the Sock Shop application services."""

# pylint: disable=duplicate-code

from .catalog import CatalogService
from .user import UserService
from .cart import CartService
from .order import OrderService
from .payment import PaymentService
from .shipping import ShippingService
from .frontend import FrontendService

__all__ = [
    "CatalogService",
    "UserService",
    "CartService",
    "OrderService",
    "PaymentService",
    "ShippingService",
    "FrontendService",
]
