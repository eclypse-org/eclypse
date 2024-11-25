"""The `ShippingService` manages the logistics and shipment of orders, ensuring items
reach customers.

- Key Responsibilities:
    - Handles the shipping of completed orders.
    - Calculates shipping costs, delivery times, and tracks shipment status.
    - Coordinates with third-party shipping providers for physical delivery.
"""

from eclypse_core.remote.communication import rest
from eclypse_core.remote.service import RESTService


class ShippingService(RESTService):
    """REST endpoints for the Shipping service."""

    @rest.endpoint("/details", "GET")
    def get_shipping_detils(self, order_id, **_):
        """Get the shipping details for an order.

        Args:
            order_id (str): The order ID.

        Returns:
            int: The HTTP status code.
            dict: The response body.

        Example:
            (200, {
                "order_id": "12345",
                "status": "success",
                "shipping_details": {
                    "carrier": "UPS",
                    "tracking_number": "1234567890",
                    "estimated_delivery_date": "2024-04-09",
                },
            })
        """

        return 200, {
            "order_id": order_id,
            "status": "success",
            "shipping_details": {
                "carrier": "UPS",
                "tracking_number": "1234567890",
                "estimated_delivery_date": "2024-04-09",
            },
        }
