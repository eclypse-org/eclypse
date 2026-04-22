"""REST endpoints for post persistence."""

from eclypse.remote.communication import rest
from eclypse.remote.communication.rest import HTTPStatusCode
from eclypse.remote.service import RESTService
from eclypse.utils import format_log_kv


class PostStorageService(RESTService):
    """Persist posts and serve timeline reads."""

    def __init__(self, service_id: str, store_step: bool = False):
        """Initialise the in-memory post store."""
        super().__init__(service_id, store_step=store_step)
        self.posts: dict[int, dict[str, object]] = {}

    @rest.endpoint("/store", "POST")
    async def store(
        self,
        post_id: int,
        creator: dict,
        text: str,
        user_mentions: list[dict],
        media: list[dict],
        shortened_urls: list[dict],
        reply_to: str,
        **payload,
    ):
        """Store the composed post and forward it to the user timeline."""
        self.logger.info(
            "Received request | " + format_log_kv(post_id=post_id, creator=creator)
        )
        post = {
            "post_id": post_id,
            "creator": creator,
            "text": text,
            "user_mentions": user_mentions,
            "media": media,
            "urls": shortened_urls,
        }
        self.posts[post_id] = post
        response = await self.rest.post(
            "UserTimelineService/write",
            **payload,
            post_id=post_id,
            creator=creator,
            post=post,
            reply_to=reply_to,
        )
        self.logger.info(
            "Received response | "
            + format_log_kv(source="UserTimelineService", body=response.body)
        )
        return HTTPStatusCode.CREATED, response.body

    @rest.endpoint("/read_many", "GET")
    def read_many(self, post_ids: list[int], **_):
        """Read a batch of posts from the in-memory store."""
        self.logger.info("Received request | " + format_log_kv(post_ids=post_ids))
        return 200, {
            "posts": [
                self.posts[post_id] for post_id in post_ids if post_id in self.posts
            ]
        }
