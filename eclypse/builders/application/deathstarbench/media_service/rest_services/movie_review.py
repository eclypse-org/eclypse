"""REST endpoints for per-movie review indexing."""

from eclypse.remote.communication import rest
from eclypse.remote.communication.rest import HTTPStatusCode
from eclypse.remote.service import RESTService
from eclypse.utils import format_log_kv


class MovieReviewService(RESTService):
    """Index reviews by movie and serve review lookups."""

    def __init__(self, service_id: str, store_step: bool = False):
        """Initialise the movie review index."""
        super().__init__(service_id, store_step=store_step)
        self.by_movie: dict[str, list[dict[str, object]]] = {}

    @rest.endpoint("/write", "POST")
    def write(self, review: dict, reply_to: str, **_):
        """Index the review by movie and return the compose-review result."""
        self.logger.info(
            "Received request | "
            + format_log_kv(review_id=review["review_id"], movie_id=review["movie_id"])
        )
        self.by_movie.setdefault(review["movie_id"], []).append(review)
        return HTTPStatusCode.CREATED, {
            "reply_to": reply_to,
            "review_id": review["review_id"],
            "movie_id": review["movie_id"],
            "movie_title": review["movie_title"],
            "status": "stored",
            "review_count": len(self.by_movie[review["movie_id"]]),
        }

    @rest.endpoint("/read", "GET")
    def read(self, movie_id: str, **_):
        """Return the indexed reviews for a movie."""
        self.logger.info("Received request | " + format_log_kv(movie_id=movie_id))
        return 200, {"reviews": self.by_movie.get(movie_id, [])}
