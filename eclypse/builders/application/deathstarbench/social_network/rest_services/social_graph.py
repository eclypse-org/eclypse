"""REST endpoints for social-graph queries."""

from eclypse.remote.communication import rest
from eclypse.remote.service import RESTService
from eclypse.utils import format_log_kv


class SocialGraphService(RESTService):
    """Return follower relationships for fan-out operations."""

    def __init__(self, service_id: str, store_step: bool = False):
        """Initialise the social-graph fixture data."""
        super().__init__(service_id, store_step=store_step)
        self.followers_map = {
            101: [202, 303],
            202: [101],
            303: [101, 202],
        }

    @rest.endpoint("/followers", "GET")
    def followers(self, user_id: int, **_):
        """Return the followers of the requested user."""
        self.logger.info("Received request | " + format_log_kv(user_id=user_id))
        return 200, {"followers": self.followers_map.get(user_id, [])}

    @rest.endpoint("/follow", "POST")
    def follow(self, user_id: int, follower_id: int, **_):
        """Add a follower relationship to the in-memory social graph."""
        self.logger.info(
            "Received request | "
            + format_log_kv(user_id=user_id, follower_id=follower_id)
        )
        self.followers_map.setdefault(user_id, [])
        if follower_id not in self.followers_map[user_id]:
            self.followers_map[user_id].append(follower_id)
        return 200, {"followers": self.followers_map[user_id]}
