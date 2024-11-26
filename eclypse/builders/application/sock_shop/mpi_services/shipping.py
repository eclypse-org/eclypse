"""The `ShippingService` manages the logistics and shipment of orders, ensuring items
reach customers.

- Key Responsibilities:
    - Handles the shipping of completed orders.
    - Calculates shipping costs, delivery times, and tracks shipment status.
    - Coordinates with third-party shipping providers for physical delivery.
"""

from eclypse_core.remote.communication import mpi
from eclypse_core.remote.service import Service


class ShippingService(Service):
    """MPI workflow of the Shipping service."""

    async def step(self):
        """Example workflow of the Shipping service, consisting of processing shipping
        requests."""
        await self.order_request()  # pylint: disable=no-value-for-parameter

    @mpi.exchange(receive=True, send=True)
    def order_request(self, sender_id, body):
        """Process the order request and send the response to the `OrderService`.

        Args:
            sender_id (str): The ID of the sender.
            body (dict): The request body.

        Returns:
            str: The ID of the recipient.
            dict: The response body.
        """

        self.logger.info(f"{self.id} - {body}")

        # Send response to OrderService
        if body.get("request_type") == "shipping_request":
            shipping_response = {
                "response_type": "shipping_response",
                "order_id": body.get("order_id"),
                "status": "success",
                "shipping_details": {
                    "carrier": "UPS",
                    "tracking_number": "1234567890",
                    "estimated_delivery_date": "2023-05-01",
                },
            }
        else:
            shipping_response = {
                "response_type": "shipping_response",
                "status": "Invalid request",
            }

        return sender_id, shipping_response
