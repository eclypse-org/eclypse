"""REST endpoints for media-service user data."""

from eclypse.remote.communication import rest
from eclypse.remote.service import RESTService
from eclypse.utils import format_log_kv


class UserService(RESTService):
    """Resolve user identities for review requests."""

    @rest.endpoint("/compose", "POST")
    async def compose(self, user_id: int, username: str, **payload):
        """Attach user metadata and store the review."""
        self.logger.info(
            "Received request | " + format_log_kv(user_id=user_id, username=username)
        )
        user = {"user_id": user_id, "username": username}
        response = await self.rest.post(
            "ReviewStorageService/store",
            **payload,
            user=user,
        )
        self.logger.info(
            "Received response | "
            + format_log_kv(source="ReviewStorageService", body=response.body)
        )
        return 200, response.body

    @rest.endpoint("/user", "GET")
    def user(self, user_id: int, username: str, **_):
        """Return a compact user descriptor for the review author."""
        self.logger.info(
            "Received request | " + format_log_kv(user_id=user_id, username=username)
        )
        return 200, {"user": {"user_id": user_id, "username": username}}
