"""REST endpoints for thumbnail creation."""

from eclypse.remote.communication import rest
from eclypse.remote.service import RESTService
from eclypse.utils import format_log_kv


class TransformService(RESTService):
    """Create thumbnail metadata from an image."""

    @rest.endpoint("/thumbnail", "POST")
    def thumbnail(self, image_id: str, resolution: list[int], **_):
        """Build thumbnail metadata for the uploaded image."""
        self.logger.info(
            "Received request | "
            + format_log_kv(image_id=image_id, resolution=resolution)
        )
        return 200, {
            "image_id": image_id,
            "thumbnail": {
                "width": resolution[0] // 6,
                "height": resolution[1] // 6,
                "format": "jpeg",
            },
        }
