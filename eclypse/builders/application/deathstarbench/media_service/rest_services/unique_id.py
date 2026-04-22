"""REST endpoints for review identifier generation."""

from eclypse.remote.communication import rest
from eclypse.remote.service import RESTService
from eclypse.utils import format_log_kv


class UniqueIdService(RESTService):
    """Assign review identifiers for compose-review requests."""

    def __init__(self, service_id: str, store_step: bool = False):
        """Initialise the review identifier counter."""
        super().__init__(service_id, store_step=store_step)
        self.next_review_id = 7000

    @rest.endpoint("/compose", "POST")
    async def compose(self, **payload):
        """Assign a review id and forward the request to movie lookup."""
        self.logger.info("Received request | " + format_log_kv(payload=payload))
        self.next_review_id += 1
        response = await self.rest.post(
            "MovieIdService/compose",
            **payload,
            review_id=self.next_review_id,
        )
        self.logger.info(
            "Received response | "
            + format_log_kv(source="MovieIdService", body=response.body)
        )
        return 200, response.body
