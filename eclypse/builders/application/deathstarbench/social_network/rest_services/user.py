"""REST endpoints for social-network user data."""

from eclypse.remote.communication import rest
from eclypse.remote.service import RESTService
from eclypse.utils import format_log_kv


class UserService(RESTService):
    """Resolve user identities for compose-post requests."""

    @rest.endpoint("/compose", "POST")
    async def compose(self, user_id: int, username: str, **payload):
        """Attach creator metadata and store the composed post."""
        self.logger.info(
            "Received request | " + format_log_kv(user_id=user_id, username=username)
        )
        creator = {"user_id": user_id, "username": username}
        response = await self.rest.post(
            "PostStorageService/store",
            **payload,
            user_id=user_id,
            username=username,
            creator=creator,
        )
        self.logger.info(
            "Received response | "
            + format_log_kv(source="PostStorageService", body=response.body)
        )
        return 200, response.body

    @rest.endpoint("/creator", "GET")
    def creator(self, user_id: int, username: str, **_):
        """Return a compact creator description for the requested user."""
        self.logger.info(
            "Received request | " + format_log_kv(user_id=user_id, username=username)
        )
        return 200, {"creator": {"user_id": user_id, "username": username}}
