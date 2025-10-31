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
    "CartService",
    "CatalogService",
    "FrontendService",
    "OrderService",
    "PaymentService",
    "ShippingService",
    "UserService",
]
