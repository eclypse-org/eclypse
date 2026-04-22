"""MPI workflow for movie identifier resolution."""

from eclypse.remote.communication import mpi
from eclypse.remote.service import Service
from eclypse.utils import format_log_kv


class MovieIdService(Service):
    """Resolve movie identifiers for review requests."""

    def __init__(self, service_id: str, store_step: bool = False):
        """Initialise the movie lookup fixture data."""
        super().__init__(service_id, store_step=store_step)
        self.movies = {
            "The Matrix": {"movie_id": "m1", "title": "The Matrix"},
            "Arrival": {"movie_id": "m2", "title": "Arrival"},
        }

    async def step(self):
        """Handle the next movie-id request."""
        await self.handle_request()  # pylint: disable=no-value-for-parameter

    @mpi.exchange(receive=True, send=True)
    def handle_request(self, sender_id, body):
        """Resolve the movie id for compose or lookup requests."""
        self.logger.info("Received request | " + format_log_kv(request=body))
        movie = self.movies[body["movie_title"]]
        if body["request_type"] == "lookup_movie":
            return sender_id, {
                "response_type": "lookup_movie_response",
                **movie,
            }
        return "TextService", {
            **body,
            "movie_id": movie["movie_id"],
        }
