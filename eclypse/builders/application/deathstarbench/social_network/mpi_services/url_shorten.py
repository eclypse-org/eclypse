"""MPI workflow for URL shortening."""

from eclypse.remote.communication import mpi
from eclypse.remote.service import Service
from eclypse.utils import format_log_kv


class UrlShortenService(Service):
    """Shorten URLs contained in a social-network post."""

    async def step(self):
        """Handle the next URL-shortening request."""
        await self.compose_request()  # pylint: disable=no-value-for-parameter

    @mpi.exchange(receive=True, send=True)
    def compose_request(self, _sender_id, body):
        """Shorten URLs and forward the workflow to media handling."""
        self.logger.info("Received request | " + format_log_kv(request=body))
        return "MediaService", {
            **body,
            "shortened_urls": [
                {"expanded_url": url, "shortened_url": f"https://t.ec/{idx}"}
                for idx, url in enumerate(body["urls"], start=1)
            ],
        }
