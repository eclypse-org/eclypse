"""MPI workflow for review persistence."""

from eclypse.remote.communication import mpi
from eclypse.remote.service import Service
from eclypse.utils import format_log_kv


class ReviewStorageService(Service):
    """Persist reviews and provide review lookups."""

    def __init__(self, service_id: str, store_step: bool = False):
        """Initialise the in-memory review store."""
        super().__init__(service_id, store_step=store_step)
        self.reviews: dict[int, dict[str, object]] = {}

    async def step(self):
        """Handle the next review-storage request."""
        await self.handle_request()  # pylint: disable=no-value-for-parameter

    @mpi.exchange(receive=True, send=True)
    def handle_request(self, sender_id, body):
        """Store reviews or return a batch of stored reviews."""
        self.logger.info("Received request | " + format_log_kv(request=body))
        if body["request_type"] == "read_reviews":
            return sender_id, {
                "response_type": "read_reviews_response",
                "reviews": [
                    self.reviews[review_id]
                    for review_id in body["review_ids"]
                    if review_id in self.reviews
                ],
            }

        review = {
            "review_id": body["review_id"],
            "movie_id": body["movie_id"],
            "movie_title": body["movie_title"],
            "rating": body["rating"],
            "text": body["text"],
            "user": body["user"],
        }
        self.reviews[body["review_id"]] = review
        return "UserReviewService", {
            **body,
            "request_type": "write_user_review",
            "review": review,
        }
