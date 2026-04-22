"""REST endpoints for movie plot metadata."""

from eclypse.remote.communication import rest
from eclypse.remote.service import RESTService
from eclypse.utils import format_log_kv


class PlotService(RESTService):
    """Return plot metadata for a movie."""

    @rest.endpoint("/plot", "GET")
    def plot(self, movie_id: str, **_):
        """Return a short plot summary for the requested movie."""
        self.logger.info("Received request | " + format_log_kv(movie_id=movie_id))
        plots = {
            "m1": "A hacker discovers the world is a simulation.",
            "m2": "A linguist learns to communicate with alien visitors.",
        }
        return 200, {"plot": plots.get(movie_id, "")}
