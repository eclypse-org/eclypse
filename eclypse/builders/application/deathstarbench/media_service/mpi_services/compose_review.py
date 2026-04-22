"""MPI workflow for movie-review composition."""

from eclypse.remote.communication import mpi
from eclypse.remote.service import Service
from eclypse.utils import format_log_kv


class ComposeReviewService(Service):
    """Drive one media-service compose-review workflow."""

    def __init__(self, service_id: str, store_step: bool = False):
        """Initialise the compose-review workflow state."""
        super().__init__(service_id, store_step=store_step)
        self.req_id = 0
        self.user_id = 101
        self.username = "ada"

    async def step(self):
        """Start the compose-review workflow and await the final response."""
        self.req_id += 1
        await self.submit_review()
        response = await self.mpi.recv()
        self.logger.info("Received response | " + format_log_kv(response=response))
        return response

    @mpi.exchange(send=True)
    def submit_review(self):
        """Send a compose-review request into the media-service pipeline."""
        return "UniqueIdService", {
            "request_type": "compose_review",
            "reply_to": self.id,
            "req_id": self.req_id,
            "user_id": self.user_id,
            "username": self.username,
            "movie_title": "The Matrix",
            "rating": 5,
            "text": "A sharp and timeless science-fiction classic.",
        }
