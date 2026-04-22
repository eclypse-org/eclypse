"""REST endpoints for review text processing."""

from eclypse.remote.communication import rest
from eclypse.remote.service import RESTService
from eclypse.utils import format_log_kv


class TextService(RESTService):
    """Normalise review text before storing the review."""

    @rest.endpoint("/compose", "POST")
    async def compose(self, text: str, **payload):
        """Normalise review text and forward the request to rating handling."""
        self.logger.info("Received request | " + format_log_kv(text=text))
        response = await self.rest.post(
            "RatingService/compose",
            **payload,
            text=text.strip(),
        )
        self.logger.info(
            "Received response | "
            + format_log_kv(source="RatingService", body=response.body)
        )
        return 200, response.body
