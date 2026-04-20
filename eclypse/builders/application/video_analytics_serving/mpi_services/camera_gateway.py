"""MPI workflow for the camera gateway service."""

from eclypse.remote.communication import mpi
from eclypse.remote.service import Service
from eclypse.utils import format_log_kv


class CameraGatewayService(Service):
    """Entry-point service that starts the video analytics pipeline."""

    def __init__(self, service_id: str, store_step: bool = False):
        """Initialise the gateway with a rolling frame counter."""
        super().__init__(service_id, store_step=store_step)
        self.frame_id = 0

    async def step(self):
        """Capture the next frame and wait for the analytics summary."""
        self.frame_id += 1
        await self.start_pipeline()
        response = await self.mpi.recv()
        self.logger.info("Received response | " + format_log_kv(response=response))
        return response

    @mpi.exchange(send=True)
    def start_pipeline(self):
        """Send a synthetic frame to the detection service."""
        return "DetectionService", {
            "request_type": "analyse_frame",
            "frame_id": self.frame_id,
            "stream_id": "camera-a",
            "objects": ["person", "forklift"],
        }
