"""MPI workflow for social-network post composition."""

from eclypse.remote.communication import mpi
from eclypse.remote.service import Service
from eclypse.utils import format_log_kv


class ComposePostService(Service):
    """Drive one social-network compose-post workflow."""

    def __init__(self, service_id: str, store_step: bool = False):
        """Initialise the compose-post workflow state."""
        super().__init__(service_id, store_step=store_step)
        self.req_id = 0
        self.user_id = 101
        self.username = "alice"

    async def step(self):
        """Start the compose-post workflow and await the final response."""
        self.req_id += 1
        await self.submit_post()
        response = await self.mpi.recv()
        self.logger.info("Received response | " + format_log_kv(response=response))
        return response

    @mpi.exchange(send=True)
    def submit_post(self):
        """Send a compose-post request into the social-network pipeline."""
        return "UniqueIdService", {
            "request_type": "compose_post",
            "reply_to": self.id,
            "req_id": self.req_id,
            "user_id": self.user_id,
            "username": self.username,
            "text": "Hello @bob check https://example.com",
            "media_ids": [11],
            "media_types": ["image"],
            "post_type": "POST",
        }
