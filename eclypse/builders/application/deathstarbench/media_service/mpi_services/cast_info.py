"""MPI workflow for movie cast metadata."""

from eclypse.remote.communication import mpi
from eclypse.remote.service import Service
from eclypse.utils import format_log_kv


class CastInfoService(Service):
    """Return cast metadata for a movie."""

    async def step(self):
        """Handle the next cast-info request."""
        await self.handle_request()  # pylint: disable=no-value-for-parameter

    @mpi.exchange(receive=True, send=True)
    def handle_request(self, sender_id, body):
        """Return a small cast list for the requested movie."""
        self.logger.info("Received request | " + format_log_kv(request=body))
        casts = {
            "m1": ["Keanu Reeves", "Carrie-Anne Moss"],
            "m2": ["Amy Adams", "Jeremy Renner"],
        }
        return sender_id, {
            "response_type": "cast_response",
            "cast": casts.get(body["movie_id"], []),
        }
