"""The `CartService` handles the shopping cart functionality, allowing users to manage \
their desired items before making a purchase.

- Key Responsibilities:
    - Manages the user’s shopping cart by adding, removing, or updating items.
    - Stores cart data temporarily for guest users or long-term for registered users.
"""

from eclypse_core.remote.communication import rest
from eclypse_core.remote.service import RESTService


class CartService(RESTService):
    """REST endpoints for the Cart service."""

    @rest.endpoint("/cart", "GET")
    def get_cart(self, **_):
        """Get the user's shopping cart.

        Returns:
            int: The HTTP status code.
            dict: The response body.

        Example:
            (200, {
                "items": [
                    {"id": "1", "quantity": 2},
                    {"id": "2", "quantity": 1},
                ],
            })
        """
        return 200, {
            "items": [
                {"id": "1", "quantity": 2},
                {"id": "2", "quantity": 1},
            ],
        }
