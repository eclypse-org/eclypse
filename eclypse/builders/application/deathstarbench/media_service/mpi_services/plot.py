"""MPI workflow for movie plot metadata."""

from eclypse.remote.communication import mpi
from eclypse.remote.service import Service
from eclypse.utils import format_log_kv


class PlotService(Service):
    """Return plot metadata for a movie."""

    async def step(self):
        """Handle the next plot-info request."""
        await self.handle_request()  # pylint: disable=no-value-for-parameter

    @mpi.exchange(receive=True, send=True)
    def handle_request(self, sender_id, body):
        """Return a short plot summary for the requested movie."""
        self.logger.info("Received request | " + format_log_kv(request=body))
        plots = {
            "m1": "A hacker discovers the world is a simulation.",
            "m2": "A linguist learns to communicate with alien visitors.",
        }
        return sender_id, {
            "response_type": "plot_response",
            "plot": plots.get(body["movie_id"], ""),
        }
