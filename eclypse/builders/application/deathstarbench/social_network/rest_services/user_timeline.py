"""REST endpoints for user-timeline management."""

from eclypse.remote.communication import rest
from eclypse.remote.service import RESTService
from eclypse.utils import format_log_kv


class UserTimelineService(RESTService):
    """Store and read per-user timelines."""

    def __init__(self, service_id: str, store_step: bool = False):
        """Initialise the user timeline store."""
        super().__init__(service_id, store_step=store_step)
        self.timelines: dict[int, list[int]] = {}

    @rest.endpoint("/write", "POST")
    async def write(self, creator: dict, post_id: int, post: dict, reply_to: str, **_):
        """Append a post to the creator timeline and fan out to home timelines."""
        self.logger.info(
            "Received request | " + format_log_kv(creator=creator, post_id=post_id)
        )
        self.timelines.setdefault(creator["user_id"], []).append(post_id)
        response = await self.rest.post(
            "HomeTimelineService/write",
            creator=creator,
            post_id=post_id,
            post=post,
            reply_to=reply_to,
        )
        self.logger.info(
            "Received response | "
            + format_log_kv(source="HomeTimelineService", body=response.body)
        )
        return 200, response.body

    @rest.endpoint("/read", "GET")
    async def read(self, user_id: int, **_):
        """Read the stored posts for a user timeline."""
        self.logger.info("Received request | " + format_log_kv(user_id=user_id))
        post_ids = self.timelines.get(user_id, [])
        response = await self.rest.get(
            "PostStorageService/read_many",
            post_ids=post_ids,
        )
        self.logger.info(
            "Received response | "
            + format_log_kv(source="PostStorageService", body=response.body)
        )
        return 200, {"user_id": user_id, "posts": response.body["posts"]}
