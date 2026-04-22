"""The `FrontendService` class.

It serves as the user interface for the SockShop application,
providing the user-facing components of the store.

- Key Responsibilities:
    - Displays product catalogs, shopping carts, and order information to users.
    - Interacts with backend services (e.g., `CatalogService`,
      `UserService`, `OrderService`) to display real-time data.
    - Manages user input and interactions such as product searches,
      cart updates, and order placements.
"""

from eclypse.remote.communication import mpi
from eclypse.remote.service import Service
from eclypse.utils import format_log_kv


class FrontendService(Service):
    """MPI workflow of the Frontend service."""

    def __init__(self, name, store_step: bool = False):
        """Initialize the FrontendService with a user ID.

        Args:
            name (str): The name of the service.
            store_step (bool, optional): Whether to store the results of
                each step. Defaults to False.
        """
        super().__init__(name, store_step=store_step)
        self.user_id = 12345

    async def step(self):
        """Example workflow of the `Frontend` service.

        It starts with fetching the catalog, user data, and cart items,
        then placing an order.
        """
        # Send request to CatalogService
        await self.catalog_request()

        # Receive response from CatalogService
        catalog_response = await self.mpi.recv()

        self.logger.info(
            "Received response | "
            + format_log_kv(source="CatalogService", body=catalog_response)
        )

        # Send request to UserService
        user_request = {"request_type": "user_data", "user_id": self.user_id}
        self.mpi.send("UserService", user_request)

        # Receive response from UserService
        user_response = await self.mpi.recv()
        self.logger.info(
            "Received response | "
            + format_log_kv(source="UserService", body=user_response)
        )

        # Send request to CartService
        cart_request = {"request_type": "cart_data", "user_id": self.user_id}
        self.mpi.send("CartService", cart_request)

        # Receive response from CartService
        cart_response = await self.mpi.recv()
        self.logger.info(
            "Received response | "
            + format_log_kv(source="CartService", body=cart_response)
        )

        products = catalog_response.get("products", [])
        cart_items = cart_response.get("items", [])
        order_items = [
            {
                "id": item["id"],
                "amount": next(
                    (
                        product["price"] * item["quantity"]
                        for product in products
                        if product["id"] == item["id"]
                    ),
                    0.0,
                ),
            }
            for item in cart_items
        ]

        # Send request to OrderService
        order_request = {
            "request_type": "order_request",
            "user_id": self.user_id,
            "items": order_items,
        }
        self.mpi.send("OrderService", order_request)

        # Receive response from OrderService
        order_response = await self.mpi.recv()
        self.logger.info(
            "Received response | "
            + format_log_kv(source="OrderService", body=order_response)
        )

    @mpi.exchange(send=True)
    def catalog_request(self):
        """Send a request to the CatalogService for product data.

        Returns:
            str: The recipient service name.
            dict: The request body.
        """
        return "CatalogService", {"request_type": "catalog_data"}
