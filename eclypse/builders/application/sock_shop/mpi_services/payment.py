"""The `PaymentService` class.

It is responsible for handling all payment-related transactions in the SockShop.

- Key Responsibilities:
    - Processes payment details and initiates transactions for placed orders.
    - Communicates with external payment providers and returns transaction statuses \
        (e.g., success, failure).
"""

import random as rnd

from eclypse.remote.communication import mpi
from eclypse.remote.service import Service
from eclypse.utils import format_log_kv


class PaymentService(Service):
    """MPI workflow of the Payment service."""

    async def step(self):
        """Example workflow of the `PaymentService` class.

        It consists of processing payment requests.
        """
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
        self.logger.info("Received request | " + format_log_kv(request=body))

        # Send response to OrderService
        if body.get("request_type") == "payment_request":
            payment_response = {
                "response_type": "payment_response",
                "order_id": body.get("order_id"),
                "transaction_id": rnd.randint(1000, 9999),
                "status": "success" if rnd.choice([True, False]) else "failure",
            }
        else:
            payment_response = {
                "response_type": "payment_response",
                "status": "Invalid request",
            }

        return sender_id, payment_response
