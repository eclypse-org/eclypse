"""The `PaymentService` is responsible for handling all payment-related transactions in
the SockShop.

- Key Responsibilities:
    - Processes payment details and initiates transactions for placed orders.
    - Communicates with external payment providers and returns transaction statuses (e.g., success, failure).
"""

import random as rnd

from eclypse_core.remote.communication import mpi
from eclypse_core.remote.service import Service


class PaymentService(Service):
    """MPI workflow of the Payment service."""

    async def step(self):
        """Example workflow of the Payment service, consisting of processing payment
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
        if body.get("request_type") == "payment_request":
            payment_response = {
                "response_type": "payment_response",
                "order_id": body.get("order_id"),
                "status": "success" if rnd.choice([True, False]) else "failure",
            }
        else:
            payment_response = {
                "response_type": "payment_response",
                "status": "Invalid request",
            }

        return sender_id, payment_response
