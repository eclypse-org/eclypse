"""REST endpoints for upload notification."""

from eclypse.remote.communication import rest
from eclypse.remote.service import RESTService
from eclypse.utils import format_log_kv


class NotificationService(RESTService):
    """Return the final thumbnail location."""

    @rest.endpoint("/notify", "POST")
    def notify(self, image_id: str, uri: str, **_):
        """Return the final storage location for the generated thumbnail."""
        self.logger.info(
            "Received request | " + format_log_kv(image_id=image_id, uri=uri)
        )
        return 200, {
            "image_id": image_id,
            "uri": uri,
            "status": "stored",
        }
