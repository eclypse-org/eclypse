"""REST workflow for movie-review composition."""

from eclypse.remote.service import Service
from eclypse.utils import format_log_kv


class ComposeReviewService(Service):
    """Drive one media-service compose-review workflow."""

    def __init__(self, service_id: str, store_step: bool = False):
        """Initialise the compose-review workflow state."""
        super().__init__(
            service_id,
            communication_interface="rest",
            store_step=store_step,
        )
        self.req_id = 0
        self.user_id = 101
        self.username = "ada"

    async def step(self):
        """Compose a review and trigger the downstream review pipeline."""
        self.req_id += 1
        response = await self.rest.post(
            "UniqueIdService/compose",
            req_id=self.req_id,
            reply_to=self.id,
            user_id=self.user_id,
            username=self.username,
            movie_title="The Matrix",
            rating=5,
            text="A sharp and timeless science-fiction classic.",
        )
        self.logger.info(
            "Received response | "
            + format_log_kv(source="UniqueIdService", body=response.body)
        )
        return response
