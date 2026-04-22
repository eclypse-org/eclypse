"""MPI workflow for post persistence."""

from eclypse.remote.communication import mpi
from eclypse.remote.service import Service
from eclypse.utils import format_log_kv


class PostStorageService(Service):
    """Persist posts and serve timeline reads."""

    def __init__(self, service_id: str, store_step: bool = False):
        """Initialise the in-memory post store."""
        super().__init__(service_id, store_step=store_step)
        self.posts: dict[int, dict[str, object]] = {}

    async def step(self):
        """Handle the next post-storage request."""
        await self.handle_request()  # pylint: disable=no-value-for-parameter

    @mpi.exchange(receive=True, send=True)
    def handle_request(self, sender_id, body):
        """Store posts or return a batch of posts to the requester."""
        self.logger.info("Received request | " + format_log_kv(request=body))
        if body["request_type"] == "read_posts":
            return sender_id, {
                "response_type": "read_posts_response",
                "posts": [
                    self.posts[post_id]
                    for post_id in body["post_ids"]
                    if post_id in self.posts
                ],
            }

        post = {
            "post_id": body["post_id"],
            "creator": body["creator"],
            "text": body["text"],
            "user_mentions": body["user_mentions"],
            "media": body["media"],
            "urls": body["shortened_urls"],
        }
        self.posts[body["post_id"]] = post
        return "UserTimelineService", {
            **body,
            "request_type": "write_user_timeline",
            "post": post,
        }
