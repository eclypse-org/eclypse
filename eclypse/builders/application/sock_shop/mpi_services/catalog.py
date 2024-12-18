"""The `CatalogService` is responsible for managing and serving product information.

- Key Responsibilities:
    -
    - Supports operations such as searching for products and listing available items \
    in the store.
    - Interfaces with the underlying data store to fetch product data.
"""

from eclypse_core.remote.communication import mpi
from eclypse_core.remote.service import Service


class CatalogService(Service):
    """MPI workflows for the Catalog service."""

    async def step(self):
        """The `CatalogService` workflow consists of receiving a request from the \
        `FrontendService` and sending a response containing product information."""

        await self.frontend_request()  # pylint: disable=no-value-for-parameter

    @mpi.exchange(receive=True, send=True)
    def frontend_request(self, sender_id, body):
        """Process requests from the FrontendService and send responses back.

        Args:
            sender_id (str): The ID of the sender.
            body (dict): The request body.

        Returns:
            str: The ID of the recipient.
            dict: The response body.
        """
        self.logger.info(f"{self.id} - {body}")

        # Send response to FrontendService
        if body.get("request_type") == "catalog_data":

            frontend_response = {
                "response_type": "catalog_response",
                "products": [
                    {"id": "1", "name": "Product 1", "price": 19.99},
                    {"id": "2", "name": "Product 2", "price": 29.99},
                ],
            }
        else:
            frontend_response = {
                "response_type": "catalog_response",
                "status": "Invalid request",
            }

        return sender_id, frontend_response
