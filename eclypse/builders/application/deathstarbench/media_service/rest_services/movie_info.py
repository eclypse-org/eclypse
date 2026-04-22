"""REST endpoints for aggregated movie information."""

from eclypse.remote.communication import rest
from eclypse.remote.service import RESTService
from eclypse.utils import format_log_kv


class MovieInfoService(RESTService):
    """Aggregate movie metadata and reviews."""

    @rest.endpoint("/details", "GET")
    async def details(self, movie_id: str, movie_title: str, **_):
        """Return a combined view of cast, plot, and stored reviews."""
        self.logger.info(
            "Received request | "
            + format_log_kv(movie_id=movie_id, movie_title=movie_title)
        )
        cast = await self.rest.get("CastInfoService/cast", movie_id=movie_id)
        self.logger.info(
            "Received response | "
            + format_log_kv(source="CastInfoService", body=cast.body)
        )
        plot = await self.rest.get("PlotService/plot", movie_id=movie_id)
        self.logger.info(
            "Received response | " + format_log_kv(source="PlotService", body=plot.body)
        )
        reviews = await self.rest.get("MovieReviewService/read", movie_id=movie_id)
        self.logger.info(
            "Received response | "
            + format_log_kv(source="MovieReviewService", body=reviews.body)
        )
        return 200, {
            "movie_id": movie_id,
            "movie_title": movie_title,
            "cast": cast.body["cast"],
            "plot": plot.body["plot"],
            "reviews": reviews.body["reviews"],
        }
