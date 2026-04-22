"""REST endpoints for home-timeline fan-out."""

from eclypse.remote.communication import rest
from eclypse.remote.communication.rest import HTTPStatusCode
from eclypse.remote.service import RESTService
from eclypse.utils import format_log_kv


class HomeTimelineService(RESTService):
    """Fan out posts to follower home timelines."""

    def __init__(self, service_id: str, store_step: bool = False):
        """Initialise the home timeline store."""
        super().__init__(service_id, store_step=store_step)
        self.timelines: dict[int, list[int]] = {}

    @rest.endpoint("/write", "POST")
    async def write(self, creator: dict, post_id: int, reply_to: str, **payload):
        """Fan out the stored post to followers of the creator."""
        self.logger.info(
            "Received request | " + format_log_kv(creator=creator, post_id=post_id)
        )
        followers = await self.rest.get(
            "SocialGraphService/followers",
            user_id=creator["user_id"],
        )
        self.logger.info(
            "Received response | "
            + format_log_kv(source="SocialGraphService", body=followers.body)
        )
        home_receivers = [creator["user_id"], *followers.body["followers"]]
        for user_id in home_receivers:
            self.timelines.setdefault(user_id, []).append(post_id)
        return HTTPStatusCode.CREATED, {
            "reply_to": reply_to,
            "post_id": post_id,
            "follower_count": len(followers.body["followers"]),
            "delivered_to": home_receivers,
            "status": "posted",
            "text": payload["post"]["text"],
        }

    @rest.endpoint("/read", "GET")
    async def read(self, user_id: int, **_):
        """Read the home timeline for a user."""
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
