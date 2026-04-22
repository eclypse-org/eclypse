"""MPI workflow for home-timeline fan-out."""

from eclypse.remote.communication import mpi
from eclypse.remote.service import Service
from eclypse.utils import format_log_kv


class HomeTimelineService(Service):
    """Fan out posts to follower home timelines."""

    def __init__(self, service_id: str, store_step: bool = False):
        """Initialise the home timeline store."""
        super().__init__(service_id, store_step=store_step)
        self.timelines: dict[int, list[int]] = {}
        self.pending_request: dict[str, object] = {}

    async def step(self):
        """Handle the next home-timeline request."""
        await self.handle_request()
        return await self.followers_response()

    @mpi.exchange(receive=True, send=True)
    def handle_request(self, sender_id, body):
        """Request followers before fan-out completes."""
        self.logger.info("Received request | " + format_log_kv(request=body))
        self.pending_request = {
            **body,
            "sender_id": sender_id,
        }
        return "SocialGraphService", {
            "request_type": "get_followers",
            "user_id": body["creator"]["user_id"],
        }

    @mpi.exchange(receive=True, send=True)
    def followers_response(self, _sender_id, body):
        """Complete the home-timeline fan-out once followers are known."""
        self.logger.info("Received request | " + format_log_kv(request=body))
        home_receivers = [
            self.pending_request["creator"]["user_id"],
            *body["followers"],
        ]
        for user_id in home_receivers:
            self.timelines.setdefault(user_id, []).append(
                self.pending_request["post_id"],
            )
        return self.pending_request["reply_to"], {
            "response_type": "compose_post_response",
            "post_id": self.pending_request["post_id"],
            "follower_count": len(body["followers"]),
            "delivered_to": home_receivers,
            "status": "posted",
            "text": self.pending_request["post"]["text"],
        }
