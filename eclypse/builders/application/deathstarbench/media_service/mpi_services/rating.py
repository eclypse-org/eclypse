"""MPI workflow for rating validation."""

from eclypse.remote.communication import mpi
from eclypse.remote.service import Service
from eclypse.utils import format_log_kv


class RatingService(Service):
    """Validate review ratings before review storage."""

    async def step(self):
        """Handle the next rating-validation request."""
        await self.compose_request()  # pylint: disable=no-value-for-parameter

    @mpi.exchange(receive=True, send=True)
    def compose_request(self, _sender_id, body):
        """Validate the rating and forward the request to user lookup."""
        self.logger.info("Received request | " + format_log_kv(request=body))
        return "UserService", {
            **body,
            "rating": max(1, min(5, body["rating"])),
        }
