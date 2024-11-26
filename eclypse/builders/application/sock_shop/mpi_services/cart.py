"""The `CartService` handles the shopping cart functionality.

- Key Responsibilities:
    - Manages the user’s shopping cart by adding, removing, or updating items.
    - Stores cart data temporarily for guest users or long-term for registered users.
"""

from eclypse_core.remote.communication import mpi
from eclypse_core.remote.service import Service


class CartService(Service):
    """MPI workflow of the Cart service."""

    async def step(self):
        """Example workflow of the Cart service, starting with fetching the user's cart
        data."""
        await self.frontend_request()  # pylint: disable=no-value-for-parameter

    @mpi.exchange(receive=True, send=True)
    def frontend_request(self, sender_id, body):
        """Process the frontend request and send the response to the `FrontendService`.

        Args:
            sender_id (str): The ID of the sender.
            body (dict): The request body.

        Returns:
            str: The ID of the recipient.
            dict: The response body.
        """
        self.logger.info(f"{self.id} - {body}")

        # Send response to FrontendService
        if body.get("request_type") == "cart_data":
            frontend_response = {
                "response_type": "cart_response",
                "items": [
                    {"product_id": "1", "quantity": 2},
                    {"product_id": "2", "quantity": 1},
                ],
            }
        else:
            frontend_response = {
                "response_type": "cart_response",
                "status": "Invalid request",
            }

        return sender_id, frontend_response
