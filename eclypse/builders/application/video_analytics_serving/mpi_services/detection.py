"""MPI workflow for the detection service."""

from eclypse.remote.communication import mpi
from eclypse.remote.service import Service
from eclypse.utils import format_log_kv


class DetectionService(Service):
    """Detect objects in incoming frames."""

    async def step(self):
        """Handle the next frame produced by the camera gateway."""
        await self.gateway_request()  # pylint: disable=no-value-for-parameter

    @mpi.exchange(receive=True, send=True)
    def gateway_request(self, _sender_id, body):
        """Convert the incoming frame payload into detections."""
        self.logger.info("Received request | " + format_log_kv(request=body))
        return "TrackingService", {
            "request_type": "track_objects",
            "frame_id": body["frame_id"],
            "stream_id": body["stream_id"],
            "detections": body["objects"],
        }
