"""REST endpoints for review persistence."""

from eclypse.remote.communication import rest
from eclypse.remote.communication.rest import HTTPStatusCode
from eclypse.remote.service import RESTService
from eclypse.utils import format_log_kv


class ReviewStorageService(RESTService):
    """Persist reviews and provide review lookups."""

    def __init__(self, service_id: str, store_step: bool = False):
        """Initialise the in-memory review store."""
        super().__init__(service_id, store_step=store_step)
        self.reviews: dict[int, dict[str, object]] = {}

    @rest.endpoint("/store", "POST")
    async def store(
        self,
        review_id: int,
        movie_id: str,
        movie_title: str,
        rating: int,
        text: str,
        user: dict,
        reply_to: str,
        **payload,
    ):
        """Store the review and forward it to the user review index."""
        self.logger.info(
            "Received request | "
            + format_log_kv(review_id=review_id, movie_id=movie_id, user=user)
        )
        review = {
            "review_id": review_id,
            "movie_id": movie_id,
            "movie_title": movie_title,
            "rating": rating,
            "text": text,
            "user": user,
        }
        self.reviews[review_id] = review
        response = await self.rest.post(
            "UserReviewService/write",
            **payload,
            review=review,
            reply_to=reply_to,
        )
        self.logger.info(
            "Received response | "
            + format_log_kv(source="UserReviewService", body=response.body)
        )
        return HTTPStatusCode.CREATED, response.body

    @rest.endpoint("/read_many", "GET")
    def read_many(self, review_ids: list[int], **_):
        """Read a batch of reviews from the in-memory store."""
        self.logger.info("Received request | " + format_log_kv(review_ids=review_ids))
        return 200, {
            "reviews": [
                self.reviews[review_id]
                for review_id in review_ids
                if review_id in self.reviews
            ]
        }
