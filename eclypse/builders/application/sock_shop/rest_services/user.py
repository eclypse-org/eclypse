"""The `UserService` manages all user-related functionality, including registration,
authentication, and profile management.

- Key Responsibilities:
    - Handles user sign-up, login, and logout processes.
    - Manages user data, including credentials, personal information, and addresses.
"""

from eclypse_core.remote.communication import rest
from eclypse_core.remote.service import RESTService


class UserService(RESTService):
    """REST endpoints for the User service."""

    @rest.endpoint("/user", "GET")
    def get_catalog(self, user_id: int, **_):
        """Get the user's profile information.

        Args:
            user_id (int): The user's ID.

        Returns:
            int: The HTTP status code.
            dict: The response body.

        Example:
            (200, {
                "user_id": 12345,
                "name": "John Doe",
                "email": "
                "address": "123 Main St",
                "phone": "555-1234",
            })
        """

        return 200, {
            "user_id": user_id,
            "name": "John Doe",
            "email": "john@example.com",
            "address": "123 Main St",
            "phone": "555-1234",
        }
