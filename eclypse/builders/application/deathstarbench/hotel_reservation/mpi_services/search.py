"""MPI workflow for hotel search."""

from eclypse.remote.communication import mpi
from eclypse.remote.service import Service
from eclypse.utils import format_log_kv


class SearchService(Service):
    """Return a compact set of available hotels."""

    async def step(self):
        """Handle the next hotel search request from the frontend."""
        await self.frontend_request()  # pylint: disable=no-value-for-parameter

    @mpi.exchange(receive=True, send=True)
    def frontend_request(self, sender_id, body):
        """Return a curated list of hotels for the requested city."""
        self.logger.info("Received request | " + format_log_kv(request=body))
        return sender_id, {
            "response_type": "search_results",
            "city": body["city"],
            "hotels": [
                {"id": "h1", "name": "Arno View", "price": 129.0},
                {"id": "h2", "name": "Tower Stay", "price": 149.0},
            ],
        }
