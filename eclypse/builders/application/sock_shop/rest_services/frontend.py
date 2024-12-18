"""The `FrontendService` serves as the user interface for the SockShop application, \
providing the user-facing components of the store.

- Key Responsibilities:
    - Displays product catalogs, shopping carts, and order information to users.
    - Interacts with backend services \
        (e.g., `CatalogService`, `UserService`, `OrderService`) to display real-time data.
    - Manages user input and interactions such as product searches, \
        cart updates, and order placements.
"""

from eclypse_core.remote.service import Service


class FrontendService(Service):
    """Example workflow of the Frontend service."""

    def __init__(self, name):
        """Initialize the Frontend service, setting the communication interface to
        REST."""
        super().__init__(name, comm_interface="rest")
        self.user_id = 12345

    async def step(self):
        """Example workflow of the Frontend service, starting with fetching the catalog,
        user data, and cart items, then placing an order."""

        catalog_r = await self.rest.get("CatalogService/catalog")
        user_r = await self.rest.get("UserService/user", user_id=self.user_id)
        cart_r = await self.rest.get("CartService/cart")

        products = catalog_r.data.get("products", [])
        items = cart_r.data.get("items", [])
        user_data = user_r.body
        self.logger.info(f"{self.id} - {user_data}")

        order_items = [
            {
                "id": item["id"],
                "amount": next(
                    (
                        product["price"] * item["quantity"]
                        for product in products
                        if product["id"] == item["id"]
                    ),
                    None,
                ),
            }
            for item in items
        ]

        order_r = await self.rest.post("OrderService/order", items=order_items)
        self.logger.info(f"{order_r.body}")
