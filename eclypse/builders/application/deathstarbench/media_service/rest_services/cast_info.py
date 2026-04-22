"""REST endpoints for movie cast metadata."""

from eclypse.remote.communication import rest
from eclypse.remote.service import RESTService
from eclypse.utils import format_log_kv


class CastInfoService(RESTService):
    """Return cast metadata for a movie."""

    @rest.endpoint("/cast", "GET")
    def cast(self, movie_id: str, **_):
        """Return a small cast list for the requested movie."""
        self.logger.info("Received request | " + format_log_kv(movie_id=movie_id))
        casts = {
            "m1": ["Keanu Reeves", "Carrie-Anne Moss"],
            "m2": ["Amy Adams", "Jeremy Renner"],
        }
        return 200, {"cast": casts.get(movie_id, [])}
