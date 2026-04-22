"""REST workflow for social network post composition."""

from eclypse.remote.service import Service
from eclypse.utils import format_log_kv


class ComposePostService(Service):
    """Drive one social-network compose-post workflow."""

    def __init__(self, service_id: str, store_step: bool = False):
        """Initialise the compose-post workflow state."""
        super().__init__(
            service_id,
            communication_interface="rest",
            store_step=store_step,
        )
        self.req_id = 0
        self.user_id = 101
        self.username = "alice"

    async def step(self):
        """Compose a post and trigger the downstream fan-out pipeline."""
        self.req_id += 1
        response = await self.rest.post(
            "UniqueIdService/compose",
            req_id=self.req_id,
            reply_to=self.id,
            username=self.username,
            user_id=self.user_id,
            text="Hello @bob check https://example.com",
            media_ids=[11],
            media_types=["image"],
            post_type="POST",
        )
        self.logger.info(
            "Received response | "
            + format_log_kv(source="UniqueIdService", body=response.body)
        )
        return response
