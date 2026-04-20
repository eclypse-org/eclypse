"""MPI workflow for authentication."""

from eclypse.remote.communication import mpi
from eclypse.remote.service import Service
from eclypse.utils import format_log_kv


class AuthService(Service):
    """Validate an API key."""

    async def step(self):
        """Handle the next authentication request from the gateway."""
        await self.gateway_request()  # pylint: disable=no-value-for-parameter

    @mpi.exchange(receive=True, send=True)
    def gateway_request(self, sender_id, body):
        """Authorise the request and return a synthetic token."""
        self.logger.info("Received request | " + format_log_kv(request=body))
        return sender_id, {
            "response_type": "auth_response",
            "token": f"token:{body['api_key']}",
            "status": "authorized",
        }
