"""MPI workflow for user profile retrieval."""

from eclypse.remote.communication import mpi
from eclypse.remote.service import Service
from eclypse.utils import format_log_kv


class ProfileService(Service):
    """Return a booking profile for the current user."""

    async def step(self):
        """Handle the next profile request from the frontend."""
        await self.frontend_request()  # pylint: disable=no-value-for-parameter

    @mpi.exchange(receive=True, send=True)
    def frontend_request(self, sender_id, body):
        """Return a compact traveller profile for the requested user."""
        self.logger.info("Received request | " + format_log_kv(request=body))
        return sender_id, {
            "response_type": "profile_response",
            "user": {
                "user_id": body["user_id"],
                "name": "Ada Lovelace",
                "loyalty_level": "gold",
            },
        }
