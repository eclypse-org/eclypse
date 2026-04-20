"""MPI workflow for upload notification."""

from eclypse.remote.communication import mpi
from eclypse.remote.service import Service
from eclypse.utils import format_log_kv


class NotificationService(Service):
    """Return the final thumbnail location."""

    async def step(self):
        """Handle the next storage confirmation emitted by the pipeline."""
        await self.storage_request()  # pylint: disable=no-value-for-parameter

    @mpi.exchange(receive=True, send=True)
    def storage_request(self, _sender_id, body):
        """Return the final storage location to the upload service."""
        self.logger.info("Received request | " + format_log_kv(request=body))
        return "UploadService", {
            "response_type": "thumbnail_ready",
            "image_id": body["image_id"],
            "uri": body["uri"],
            "status": "stored",
        }
