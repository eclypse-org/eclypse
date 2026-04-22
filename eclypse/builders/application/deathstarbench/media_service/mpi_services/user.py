"""MPI workflow for media-service user data."""

from eclypse.remote.communication import mpi
from eclypse.remote.service import Service
from eclypse.utils import format_log_kv


class UserService(Service):
    """Resolve user identities for review requests."""

    async def step(self):
        """Handle the next user-resolution request."""
        await self.compose_request()  # pylint: disable=no-value-for-parameter

    @mpi.exchange(receive=True, send=True)
    def compose_request(self, _sender_id, body):
        """Attach user metadata and forward the request to storage."""
        self.logger.info("Received request | " + format_log_kv(request=body))
        return "ReviewStorageService", {
            **body,
            "user": {
                "user_id": body["user_id"],
                "username": body["username"],
            },
        }
