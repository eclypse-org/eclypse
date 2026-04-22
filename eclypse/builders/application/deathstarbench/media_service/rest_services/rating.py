"""REST endpoints for rating validation."""

from eclypse.remote.communication import rest
from eclypse.remote.service import RESTService
from eclypse.utils import format_log_kv


class RatingService(RESTService):
    """Validate review ratings before review storage."""

    @rest.endpoint("/compose", "POST")
    async def compose(self, rating: int, **payload):
        """Validate the rating and forward the request to user lookup."""
        self.logger.info("Received request | " + format_log_kv(rating=rating))
        response = await self.rest.post(
            "UserService/compose",
            **payload,
            rating=max(1, min(5, rating)),
        )
        self.logger.info(
            "Received response | "
            + format_log_kv(source="UserService", body=response.body)
        )
        return 200, response.body
