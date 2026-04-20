"""MPI workflow for image upload."""

from eclypse.remote.communication import mpi
from eclypse.remote.service import Service
from eclypse.utils import format_log_kv


class UploadService(Service):
    """Start the thumbnailing pipeline."""

    def __init__(self, service_id: str, store_step: bool = False):
        """Initialise the uploader with a rolling image counter."""
        super().__init__(service_id, store_step=store_step)
        self.image_id = 0

    async def step(self):
        """Upload the next image and wait for the final storage response."""
        self.image_id += 1
        await self.upload_image()
        response = await self.mpi.recv()
        self.logger.info("Received response | " + format_log_kv(response=response))
        return response

    @mpi.exchange(send=True)
    def upload_image(self):
        """Send a synthetic image payload to the transform service."""
        return "TransformService", {
            "request_type": "create_thumbnail",
            "image_id": f"img-{self.image_id}",
            "resolution": [1920, 1080],
        }
