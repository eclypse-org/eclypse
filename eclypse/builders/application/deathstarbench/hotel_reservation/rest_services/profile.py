"""REST endpoints for user profile retrieval."""

from eclypse.remote.communication import rest
from eclypse.remote.service import RESTService
from eclypse.utils import format_log_kv


class ProfileService(RESTService):
    """Return a booking profile for the current user."""

    @rest.endpoint("/profile", "GET")
    def profile(self, user_id: int, **_):
        """Return a compact traveller profile for the requested user."""
        self.logger.info("Received request | " + format_log_kv(user_id=user_id))
        return 200, {
            "user": {
                "user_id": user_id,
                "name": "Ada Lovelace",
                "loyalty_level": "gold",
            }
        }
