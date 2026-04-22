"""REST endpoints for media attachment composition."""

from eclypse.remote.communication import rest
from eclypse.remote.service import RESTService
from eclypse.utils import format_log_kv


class MediaService(RESTService):
    """Attach media metadata to a social-network post."""

    @rest.endpoint("/compose", "POST")
    async def compose(
        self,
        media_ids: list[int],
        media_types: list[str],
        **payload,
    ):
        """Build media descriptors and forward the compose request."""
        self.logger.info(
            "Received request | "
            + format_log_kv(media_ids=media_ids, media_types=media_types)
        )
        media = [
            {"media_id": media_id, "media_type": media_type}
            for media_id, media_type in zip(media_ids, media_types, strict=False)
        ]
        response = await self.rest.post(
            "UserService/compose",
            **payload,
            media_ids=media_ids,
            media_types=media_types,
            media=media,
        )
        self.logger.info(
            "Received response | "
            + format_log_kv(source="UserService", body=response.body)
        )
        return 200, response.body
