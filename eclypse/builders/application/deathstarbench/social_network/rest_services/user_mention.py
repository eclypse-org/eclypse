"""REST endpoints for user-mention resolution."""

from eclypse.remote.communication import rest
from eclypse.remote.service import RESTService
from eclypse.utils import format_log_kv


class UserMentionService(RESTService):
    """Resolve textual mentions into user identifiers."""

    @rest.endpoint("/compose", "POST")
    async def compose(self, mentions: list[str], **payload):
        """Resolve mentioned usernames and forward the compose request."""
        self.logger.info("Received request | " + format_log_kv(mentions=mentions))
        user_mentions = [
            {"user_id": 200 + idx, "username": mention}
            for idx, mention in enumerate(mentions, start=1)
        ]
        response = await self.rest.post(
            "UrlShortenService/compose",
            **payload,
            mentions=mentions,
            user_mentions=user_mentions,
        )
        self.logger.info(
            "Received response | "
            + format_log_kv(source="UrlShortenService", body=response.body)
        )
        return 200, response.body
