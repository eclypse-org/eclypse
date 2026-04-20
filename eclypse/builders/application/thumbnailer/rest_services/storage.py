"""REST endpoints for thumbnail storage."""

from eclypse.remote.communication import rest
from eclypse.remote.service import RESTService
from eclypse.utils import format_log_kv


class StorageService(RESTService):
    """Store thumbnail metadata."""

    @rest.endpoint("/store", "POST")
    def store(self, image_id: str, thumbnail: dict, **_):
        """Persist thumbnail metadata and report its storage URI."""
        self.logger.info(
            "Received request | "
            + format_log_kv(image_id=image_id, thumbnail=thumbnail)
        )
        return 200, {
            "image_id": image_id,
            "thumbnail": thumbnail,
            "uri": f"s3://thumbs/{image_id}.jpg",
        }
