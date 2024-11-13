"""The `CatalogService` is responsible for managing and serving product information.

- Key Responsibilities:
    -
    - Supports operations such as searching for products and listing available items \
    in the store.
    - Interfaces with the underlying data store to fetch product data.
"""

from eclypse_core.remote.communication import rest
from eclypse_core.remote.service import RESTService


class CatalogService(RESTService):
    """REST endpoints for the Catalog service."""

    @rest.endpoint("/catalog", "GET")
    def get_catalog(self, **_):
        """Get the catalog, including retrieving product details such as name, price,
        and description.

        Returns:
            int: The HTTP status code.
            dict: The response body.

        Example:
            (200, {
                "products": [
                    {"id": "1", "name": "Product 1", "price": 19.99},
                    {"id": "2", "name": "Product 2", "price": 29.99},
                ],
            })
        """

        return 200, {
            "products": [
                {"id": "1", "name": "Product 1", "price": 19.99},
                {"id": "2", "name": "Product 2", "price": 29.99},
            ],
        }
