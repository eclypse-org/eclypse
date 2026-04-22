"""MPI workflow for per-movie review indexing."""

from eclypse.remote.communication import mpi
from eclypse.remote.service import Service
from eclypse.utils import format_log_kv


class MovieReviewService(Service):
    """Index reviews by movie and serve review lookups."""

    def __init__(self, service_id: str, store_step: bool = False):
        """Initialise the movie review index."""
        super().__init__(service_id, store_step=store_step)
        self.by_movie: dict[str, list[dict[str, object]]] = {}

    async def step(self):
        """Handle the next movie-review request."""
        await self.handle_request()  # pylint: disable=no-value-for-parameter

    @mpi.exchange(receive=True, send=True)
    def handle_request(self, sender_id, body):
        """Index reviews by movie or return stored movie reviews."""
        self.logger.info("Received request | " + format_log_kv(request=body))
        if body["request_type"] == "read_movie_reviews":
            return sender_id, {
                "response_type": "read_movie_reviews_response",
                "reviews": self.by_movie.get(body["movie_id"], []),
            }

        self.by_movie.setdefault(body["review"]["movie_id"], []).append(body["review"])
        return body["reply_to"], {
            "response_type": "compose_review_response",
            "review_id": body["review"]["review_id"],
            "movie_id": body["review"]["movie_id"],
            "movie_title": body["review"]["movie_title"],
            "status": "stored",
            "review_count": len(self.by_movie[body["review"]["movie_id"]]),
        }
