"""MPI workflow for user-timeline management."""

from eclypse.remote.communication import mpi
from eclypse.remote.service import Service
from eclypse.utils import format_log_kv


class UserTimelineService(Service):
    """Store and read per-user timelines."""

    def __init__(self, service_id: str, store_step: bool = False):
        """Initialise the user timeline store."""
        super().__init__(service_id, store_step=store_step)
        self.timelines: dict[int, list[int]] = {}

    async def step(self):
        """Handle the next user-timeline request."""
        await self.handle_request()  # pylint: disable=no-value-for-parameter

    @mpi.exchange(receive=True, send=True)
    def handle_request(self, sender_id, body):
        """Write or read a user timeline."""
        self.logger.info("Received request | " + format_log_kv(request=body))
        if body["request_type"] == "read_user_timeline":
            return "PostStorageService", {
                "request_type": "read_posts",
                "reply_to": sender_id,
                "post_ids": self.timelines.get(body["user_id"], []),
            }

        self.timelines.setdefault(body["creator"]["user_id"], []).append(
            body["post_id"]
        )
        return "HomeTimelineService", {
            **body,
            "request_type": "write_home_timeline",
        }
