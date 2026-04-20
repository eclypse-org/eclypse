"""REST endpoints for hotel search."""

from eclypse.remote.communication import rest
from eclypse.remote.service import RESTService
from eclypse.utils import format_log_kv


class SearchService(RESTService):
    """Return a compact set of available hotels."""

    @rest.endpoint("/search", "GET")
    def search(self, city: str, nights: int, **_):
        """Return a curated list of hotels for the requested city."""
        self.logger.info(
            "Received request | " + format_log_kv(city=city, nights=nights)
        )
        return 200, {
            "city": city,
            "nights": nights,
            "hotels": [
                {"id": "h1", "name": "Arno View", "price": 129.0},
                {"id": "h2", "name": "Tower Stay", "price": 149.0},
            ],
        }
