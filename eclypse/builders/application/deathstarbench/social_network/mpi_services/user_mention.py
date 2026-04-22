"""MPI workflow for user-mention resolution."""

from eclypse.remote.communication import mpi
from eclypse.remote.service import Service
from eclypse.utils import format_log_kv


class UserMentionService(Service):
    """Resolve textual mentions into user identifiers."""

    async def step(self):
        """Handle the next mention-resolution request."""
        await self.compose_request()  # pylint: disable=no-value-for-parameter

    @mpi.exchange(receive=True, send=True)
    def compose_request(self, _sender_id, body):
        """Resolve mentions and forward the workflow to URL shortening."""
        self.logger.info("Received request | " + format_log_kv(request=body))
        return "UrlShortenService", {
            **body,
            "user_mentions": [
                {"user_id": 200 + idx, "username": mention}
                for idx, mention in enumerate(body["mentions"], start=1)
            ],
        }
