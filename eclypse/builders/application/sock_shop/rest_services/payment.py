"""The `PaymentService` is responsible for handling all payment-related transactions in
the SockShop application.

- Key Responsibilities:
    - Processes payment details and initiates transactions for placed orders.
    - Communicates with external payment providers and returns transaction statuses (e.g., success, failure).
"""

import os
import random as rnd

from eclypse_core.remote.communication import rest
from eclypse_core.remote.service import RESTService
from eclypse_core.utils.constants import RND_SEED


class PaymentService(RESTService):
    """REST service for payment processing."""

    def __init__(self, service_id: str):
        super().__init__(service_id)
        self.rnd = rnd.Random(os.getenv(RND_SEED))

    @rest.endpoint("/pay", "POST")
    def execute_payment(self, order_id: int, amount: float, **_):
        """Process the payment for the order.

        Args:
            order_id (int): The order ID.
            amount (float): The total amount to be paid.

        Returns:
            int: The HTTP status code.
            dict: The response body.

        Example:
            (200, {
                "order_id": 12345,
                "transaction_id": 54321,
                "status": "success",
            })
        """

        return 200, {
            "order_id": order_id,
            "amount": amount + self.rnd.randint(1, 10),
            "transaction_id": self.rnd.randint(1000, 9999),
            "status": "success",
        }
