"""MPI workflow for thumbnail creation."""

from eclypse.remote.communication import mpi
from eclypse.remote.service import Service
from eclypse.utils import format_log_kv


class TransformService(Service):
    """Create thumbnail metadata from an image."""

    async def step(self):
        """Handle the next image uploaded to the thumbnail pipeline."""
        await self.upload_request()  # pylint: disable=no-value-for-parameter

    @mpi.exchange(receive=True, send=True)
    def upload_request(self, _sender_id, body):
        """Create thumbnail metadata for the uploaded image."""
        self.logger.info("Received request | " + format_log_kv(request=body))
        return "StorageService", {
            "request_type": "store_thumbnail",
            "image_id": body["image_id"],
            "thumbnail": {
                "width": 320,
                "height": 180,
                "format": "jpeg",
            },
        }
