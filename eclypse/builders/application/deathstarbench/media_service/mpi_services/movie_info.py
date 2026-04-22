"""MPI workflow for aggregated movie information."""

from eclypse.remote.communication import mpi
from eclypse.remote.service import Service
from eclypse.utils import format_log_kv


class MovieInfoService(Service):
    """Aggregate movie metadata and reviews."""

    def __init__(self, service_id: str, store_step: bool = False):
        """Initialise the pending movie info request state."""
        super().__init__(service_id, store_step=store_step)
        self.pending_request: dict[str, object] = {}

    async def step(self):
        """Start a movie-info request and aggregate all downstream replies."""
        await self.request_cast()  # pylint: disable=no-value-for-parameter
        cast = await self.mpi.recv()
        self.logger.info("Received response | " + format_log_kv(response=cast))
        await self.request_plot()
        plot = await self.mpi.recv()
        self.logger.info("Received response | " + format_log_kv(response=plot))
        await self.request_reviews()
        reviews = await self.mpi.recv()
        self.logger.info("Received response | " + format_log_kv(response=reviews))
        return {
            "movie_id": self.pending_request["movie_id"],
            "movie_title": self.pending_request["movie_title"],
            "cast": cast["cast"],
            "plot": plot["plot"],
            "reviews": reviews["reviews"],
        }

    @mpi.exchange(receive=True, send=True)
    def request_cast(self, _sender_id, body):
        """Store the movie-info request and ask for cast metadata."""
        self.logger.info("Received request | " + format_log_kv(request=body))
        self.pending_request = body
        return "CastInfoService", {
            "request_type": "get_cast",
            "movie_id": body["movie_id"],
        }

    @mpi.exchange(send=True)
    def request_plot(self):
        """Request plot metadata for the pending movie."""
        return "PlotService", {
            "request_type": "get_plot",
            "movie_id": self.pending_request["movie_id"],
        }

    @mpi.exchange(send=True)
    def request_reviews(self):
        """Request reviews for the pending movie."""
        return "MovieReviewService", {
            "request_type": "read_movie_reviews",
            "movie_id": self.pending_request["movie_id"],
        }
