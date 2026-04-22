"""MPI workflow for social-graph queries."""

from eclypse.remote.communication import mpi
from eclypse.remote.service import Service
from eclypse.utils import format_log_kv


class SocialGraphService(Service):
    """Return follower relationships for fan-out operations."""

    def __init__(self, service_id: str, store_step: bool = False):
        """Initialise the social-graph fixture data."""
        super().__init__(service_id, store_step=store_step)
        self.followers_map = {
            101: [202, 303],
            202: [101],
            303: [101, 202],
        }

    async def step(self):
        """Handle the next social-graph request."""
        await self.handle_request()  # pylint: disable=no-value-for-parameter

    @mpi.exchange(receive=True, send=True)
    def handle_request(self, sender_id, body):
        """Return followers for the requested user."""
        self.logger.info("Received request | " + format_log_kv(request=body))
        return sender_id, {
            "response_type": "followers_response",
            "followers": self.followers_map.get(body["user_id"], []),
        }
