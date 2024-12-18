"""The `UserService` manages all user-related functionality, including registration,
authentication, and profile management.

- Key Responsibilities:
    - Handles user sign-up, login, and logout processes.
    - Manages user data, including credentials, personal information, and addresses.
"""

from eclypse_core.remote.communication import mpi
from eclypse_core.remote.service import Service


class UserService(Service):
    """MPI workflow of the User service."""

    async def step(self):
        """Example workflow of the User service, starting with fetching the user's
        profile information."""
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
        if body.get("request_type") == "user_data":

            frontend_response = {
                "response_type": "user_response",
                "name": "John Doe",
                "email": "john@example.com",
                "address": "123 Main St",
                "phone": "555-1234",
            }
        else:
            frontend_response = {
                "response_type": "user_response",
                "status": "Invalid request",
            }

        return sender_id, frontend_response
