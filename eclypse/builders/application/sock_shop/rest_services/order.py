"""The `OrderService` processes user orders, ensuring the coordination between \
different services like payment, inventory, and shipping.

- Key Responsibilities:
    - Creates, updates, and manages customer orders.
    - Interacts with the `PaymentService` and `ShippingService` to complete the order transaction.
    - Tracks the status of placed orders (e.g., pending, confirmed, shipped).
"""

from eclypse_core.remote.communication import rest
from eclypse_core.remote.communication.rest import HTTPStatusCode
from eclypse_core.remote.service import RESTService


class OrderService(RESTService):
    """REST endpoints for the Order service."""

    def __init__(self, name):
        super().__init__(name)
        self.order_id = 54321

    @rest.endpoint("/order", "POST")
    async def create_order(self, items, **_):
        """Create a new order for the user.

        Args:
            items (list): The list of items in the order.

        Returns:
            int: The HTTP status code.
            dict: The response body.

        Example:
            (201, {
                "order_id": "54321",
                "transaction_id": "12345",
                "shipping_details": {
                    "carrier": "UPS",
                    "tracking_number": "1234567890",
                    "estimated_delivery_date": "2024-04-09",
                },
                "status": "success",
            })
        """

        amount = sum(item["amount"] for item in items)
        payment_r = self.rest.post(
            "PaymentService/pay",
            order_id=self.order_id,
            amount=amount,
        )
        shipping_r = self.rest.get("ShippingService/details", order_id=self.order_id)

        payment_r = await payment_r
        shipping_r = await shipping_r

        shipping_details = shipping_r.body.get("shipping_details")
        transaction_id = payment_r.body.get("transaction_id")

        self.logger.info(f"{transaction_id}")

        return HTTPStatusCode.CREATED, {
            "order_id": self.order_id,
            "transaction_id": transaction_id,
            "shipping_details": shipping_details,
            "status": "success",
        }
