"""The `FrontendService` serves as the user interface for the SockShop application, \
providing the user-facing components of the store.

- Key Responsibilities:
    - Displays product catalogs, shopping carts, and order information to users.
    - Interacts with backend services \
        (e.g., `CatalogService`, `UserService`, `OrderService`) to display real-time data.
    - Manages user input and interactions such as product searches, \
        cart updates, and order placements.
"""

from eclypse_core.remote.communication import mpi
from eclypse_core.remote.service import Service


class FrontendService(Service):
    """MPI workflow of the Frontend service."""

    def __init__(self, name):
        super().__init__(name)
        self.user_id = 12345

    async def step(self):
        """Example workflow of the Frontend service, starting with fetching the catalog,
        user data, and cart items, then placing an order."""
        # Send request to CatalogService
        await self.catalog_request()

        # Receive response from CatalogService
        catalog_response = await self.mpi.recv()

        self.logger.info(f"{self.id} - {catalog_response}")

        # Send request to UserService
        user_request = {"request_type": "user_data", "user_id": self.user_id}
        self.mpi.send("UserService", user_request)

        # Receive response from UserService
        user_response = await self.mpi.recv()
        self.logger.info(f"{self.id} - {user_response}")

        # Send request to CartService
        cart_request = {"request_type": "cart_data", "user_id": self.user_id}
        self.mpi.send("CartService", cart_request)

        # Receive response from CartService
        cart_response = await self.mpi.recv()
        self.logger.info(f"{self.id} - {cart_response}")

        cart_items = cart_response.get("items", [])

        # Send request to OrderService
        order_request = {
            "request_type": "order_request",
            "user_id": self.user_id,
            "items": cart_items,
        }
        self.mpi.send("OrderService", order_request)

        # Receive response from OrderService
        order_response = await self.mpi.recv()
        self.logger.info(f"{self.id} - {order_response}")

    @mpi.exchange(send=True)
    def catalog_request(self):
        """Send a request to the CatalogService for product data.

        Returns:
            str: The recipient service name.
            dict: The request body.
        """
        return "CatalogService", {"request_type": "catalog_data"}
