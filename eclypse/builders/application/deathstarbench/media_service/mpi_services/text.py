"""MPI workflow for review text processing."""

from eclypse.remote.communication import mpi
from eclypse.remote.service import Service
from eclypse.utils import format_log_kv


class TextService(Service):
    """Normalise review text before storing the review."""

    async def step(self):
        """Handle the next text-processing request."""
        await self.compose_request()  # pylint: disable=no-value-for-parameter

    @mpi.exchange(receive=True, send=True)
    def compose_request(self, _sender_id, body):
        """Normalise review text and forward the request to ratings."""
        self.logger.info("Received request | " + format_log_kv(request=body))
        return "RatingService", {
            **body,
            "text": body["text"].strip(),
        }
