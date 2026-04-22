"""REST endpoints for URL shortening."""

from eclypse.remote.communication import rest
from eclypse.remote.service import RESTService
from eclypse.utils import format_log_kv


class UrlShortenService(RESTService):
    """Shorten URLs contained in a social-network post."""

    @rest.endpoint("/compose", "POST")
    async def compose(self, urls: list[str], **payload):
        """Shorten URLs and forward the compose request to media handling."""
        self.logger.info("Received request | " + format_log_kv(urls=urls))
        shortened_urls = [
            {"expanded_url": url, "shortened_url": f"https://t.ec/{idx}"}
            for idx, url in enumerate(urls, start=1)
        ]
        response = await self.rest.post(
            "MediaService/compose",
            **payload,
            urls=urls,
            shortened_urls=shortened_urls,
        )
        self.logger.info(
            "Received response | "
            + format_log_kv(source="MediaService", body=response.body)
        )
        return 200, response.body
