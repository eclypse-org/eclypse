# pylint: disable=no-value-for-parameter
"""The `OrderService` class.

It processes user orders, ensuring the coordination between different services
like payment, inventory, and shipping.

- Key Responsibilities:
    - Creates, updates, and manages customer orders.
    - Interacts with the `PaymentService` and `ShippingService` to
      complete the order transaction.
    - Tracks the status of placed orders (e.g., pending, confirmed, shipped).
"""

from eclypse.remote.communication import mpi
from eclypse.remote.service import Service
from eclypse.utils import format_log_kv


class OrderService(Service):
    """MPI workflow of the Order service."""

    def __init__(self, name, store_step: bool = False):
        """Initialize the OrderService with an order ID.

        Args:
            name (str): The name of the service.
            store_step (bool, optional): Whether to store the results of
                each step. Defaults to False.
        """
        super().__init__(name, store_step=store_step)
        self.order_id = 54321
        self.transaction_id: int | None = None
        self.shipping_details: dict[str, str] = {}
        self.items: list[dict[str, int]] = []

    async def step(self):
        """Example workflow of the `OrderService` class.

        It starts with processing the order request, then sending requests to the
        `PaymentService` and `ShippingService`.
        """
        await self.frontend_request()
        await self.payment_request()
        await self.shipping_request()

    @mpi.exchange(receive=True, send=True)
    def frontend_request(self, _, body):
        """Process the frontend request and send the response to the `PaymentService`.

        Args:
            body (dict): The request body.

        Returns:
            str: The ID of the recipient.
            dict: The response body.
        """
        self.logger.info("Received request | " + format_log_kv(request=body))

        self.items = body.get("items", [])
        total_amount = sum(item.get("amount", 0.0) for item in self.items)

        # Send request to PaymentService
        payment_request = {
            "request_type": "payment_request",
            "order_id": self.order_id,
            "amount": total_amount,
        }

        return "PaymentService", payment_request

    @mpi.exchange(receive=True, send=True)
    def payment_request(self, _, body):
        """Process the payment request and send the response to the `ShippingService`.

        Args:
            body (dict): The request body.

        Returns:
            str: The ID of the recipient.
            dict: The response body.
        """
        self.logger.info("Received request | " + format_log_kv(request=body))

        self.transaction_id = body.get("transaction_id")
        self.logger.info(
            "Received response | " + format_log_kv(source="PaymentService", body=body)
        )
        # Send request to ShippingService
        shipping_request = {
            "request_type": "shipping_request",
            "order_id": self.order_id,
        }

        return "ShippingService", shipping_request

    @mpi.exchange(receive=True, send=True)
    def shipping_request(self, _, body):
        """Process the shipping request and send the response to the `FrontendService`.

        Args:
            body (dict): The request body.

        Returns:
            str: The ID of the recipient.
            dict: The response body.
        """
        self.logger.info("Received request | " + format_log_kv(request=body))

        self.shipping_details = body.get("details")
        self.logger.info(
            "Received response | " + format_log_kv(source="ShippingService", body=body)
        )

        # Send response to FrontendService
        if self.transaction_id is not None:
            order_response = {
                "response_type": "order_response",
                "status": "success",
                "shipping_details": self.shipping_details,
                "transaction_id": self.transaction_id,
            }
        else:
            order_response = {
                "response_type": "order_response",
                "status": "failure",
            }

        return "FrontendService", order_response
