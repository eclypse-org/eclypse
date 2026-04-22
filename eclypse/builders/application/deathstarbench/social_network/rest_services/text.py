"""REST endpoints for text parsing and enrichment."""

import re

from eclypse.remote.communication import rest
from eclypse.remote.service import RESTService
from eclypse.utils import format_log_kv

_MENTION_RE = re.compile(r"@([a-zA-Z0-9_]+)")
_URL_RE = re.compile(r"https?://[^\\s]+")


class TextService(RESTService):
    """Extract mentions and URLs from post text."""

    @rest.endpoint("/compose", "POST")
    async def compose(self, text: str, **payload):
        """Parse the post text and forward enriched state downstream."""
        self.logger.info("Received request | " + format_log_kv(text=text))
        mentions = _MENTION_RE.findall(text)
        urls = _URL_RE.findall(text)
        response = await self.rest.post(
            "UserMentionService/compose",
            **payload,
            text=text,
            mentions=mentions,
            urls=urls,
        )
        self.logger.info(
            "Received response | "
            + format_log_kv(source="UserMentionService", body=response.body)
        )
        return 200, response.body
