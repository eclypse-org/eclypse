"""REST endpoints for social network identifier generation."""

from eclypse.remote.communication import rest
from eclypse.remote.service import RESTService
from eclypse.utils import format_log_kv


class UniqueIdService(RESTService):
    """Assign post identifiers for compose-post requests."""

    def __init__(self, service_id: str, store_step: bool = False):
        """Initialise the identifier counter."""
        super().__init__(service_id, store_step=store_step)
        self.next_post_id = 5000

    @rest.endpoint("/compose", "POST")
    async def compose(self, **payload):
        """Assign a post id and forward the compose request to the text stage."""
        self.logger.info("Received request | " + format_log_kv(payload=payload))
        self.next_post_id += 1
        response = await self.rest.post(
            "TextService/compose",
            **payload,
            post_id=self.next_post_id,
        )
        self.logger.info(
            "Received response | "
            + format_log_kv(source="TextService", body=response.body)
        )
        return 200, response.body
