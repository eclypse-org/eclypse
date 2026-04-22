"""REST endpoints for movie identifier resolution."""

from eclypse.remote.communication import rest
from eclypse.remote.service import RESTService
from eclypse.utils import format_log_kv


class MovieIdService(RESTService):
    """Resolve movie identifiers for review requests."""

    def __init__(self, service_id: str, store_step: bool = False):
        """Initialise the movie lookup fixture data."""
        super().__init__(service_id, store_step=store_step)
        self.movies = {
            "The Matrix": {"movie_id": "m1", "title": "The Matrix"},
            "Arrival": {"movie_id": "m2", "title": "Arrival"},
        }

    @rest.endpoint("/compose", "POST")
    async def compose(self, movie_title: str, **payload):
        """Resolve the movie id and forward the request to text parsing."""
        self.logger.info("Received request | " + format_log_kv(movie_title=movie_title))
        movie = self.movies[movie_title]
        response = await self.rest.post(
            "TextService/compose",
            **payload,
            movie_title=movie_title,
            movie_id=movie["movie_id"],
        )
        self.logger.info(
            "Received response | "
            + format_log_kv(source="TextService", body=response.body)
        )
        return 200, response.body

    @rest.endpoint("/lookup", "GET")
    def lookup(self, movie_title: str, **_):
        """Return the movie descriptor for the requested title."""
        self.logger.info("Received request | " + format_log_kv(movie_title=movie_title))
        return 200, self.movies[movie_title]
