"""MPI workflow for social-network user data."""

from eclypse.remote.communication import mpi
from eclypse.remote.service import Service
from eclypse.utils import format_log_kv


class UserService(Service):
    """Resolve user identities for compose-post requests."""

    async def step(self):
        """Handle the next user-resolution request."""
        await self.compose_request()  # pylint: disable=no-value-for-parameter

    @mpi.exchange(receive=True, send=True)
    def compose_request(self, _sender_id, body):
        """Attach creator metadata and forward the workflow to storage."""
        self.logger.info("Received request | " + format_log_kv(request=body))
        return "PostStorageService", {
            **body,
            "creator": {
                "user_id": body["user_id"],
                "username": body["username"],
            },
        }
