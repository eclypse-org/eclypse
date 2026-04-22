"""MPI workflow for per-user review indexing."""

from eclypse.remote.communication import mpi
from eclypse.remote.service import Service
from eclypse.utils import format_log_kv


class UserReviewService(Service):
    """Index reviews by author."""

    def __init__(self, service_id: str, store_step: bool = False):
        """Initialise the user review index."""
        super().__init__(service_id, store_step=store_step)
        self.by_user: dict[int, list[int]] = {}

    async def step(self):
        """Handle the next user-review request."""
        await self.handle_request()  # pylint: disable=no-value-for-parameter

    @mpi.exchange(receive=True, send=True)
    def handle_request(self, _sender_id, body):
        """Index the review by user and forward it to the movie review index."""
        self.logger.info("Received request | " + format_log_kv(request=body))
        self.by_user.setdefault(body["review"]["user"]["user_id"], []).append(
            body["review"]["review_id"],
        )
        return "MovieReviewService", {
            **body,
            "request_type": "write_movie_review",
        }
