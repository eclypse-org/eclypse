"""REST endpoints for per-user review indexing."""

from eclypse.remote.communication import rest
from eclypse.remote.service import RESTService
from eclypse.utils import format_log_kv


class UserReviewService(RESTService):
    """Index reviews by author."""

    def __init__(self, service_id: str, store_step: bool = False):
        """Initialise the user review index."""
        super().__init__(service_id, store_step=store_step)
        self.by_user: dict[int, list[int]] = {}

    @rest.endpoint("/write", "POST")
    async def write(self, review: dict, reply_to: str, **_):
        """Index the review by user and forward it to the movie review index."""
        self.logger.info(
            "Received request | "
            + format_log_kv(review_id=review["review_id"], user=review["user"])
        )
        self.by_user.setdefault(review["user"]["user_id"], []).append(
            review["review_id"]
        )
        response = await self.rest.post(
            "MovieReviewService/write",
            review=review,
            reply_to=reply_to,
        )
        self.logger.info(
            "Received response | "
            + format_log_kv(source="MovieReviewService", body=response.body)
        )
        return 200, response.body
