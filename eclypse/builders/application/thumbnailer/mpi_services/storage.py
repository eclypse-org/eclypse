"""MPI workflow for thumbnail storage."""

from eclypse.remote.communication import mpi
from eclypse.remote.service import Service
from eclypse.utils import format_log_kv


class StorageService(Service):
    """Store thumbnail metadata."""

    async def step(self):
        """Handle the next thumbnail metadata payload."""
        await self.transform_request()  # pylint: disable=no-value-for-parameter

    @mpi.exchange(receive=True, send=True)
    def transform_request(self, _sender_id, body):
        """Persist the thumbnail metadata and publish its storage URI."""
        self.logger.info("Received request | " + format_log_kv(request=body))
        return "NotificationService", {
            "request_type": "notify_upload",
            "image_id": body["image_id"],
            "uri": f"s3://thumbs/{body['image_id']}.jpg",
        }
