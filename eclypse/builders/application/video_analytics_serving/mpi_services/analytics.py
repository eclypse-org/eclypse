"""MPI workflow for the analytics service."""

from eclypse.remote.communication import mpi
from eclypse.remote.service import Service
from eclypse.utils import format_log_kv


class AnalyticsService(Service):
    """Aggregate tracked events into a compact result."""

    async def step(self):
        """Handle the next tracking result emitted by the pipeline."""
        await self.tracking_request()  # pylint: disable=no-value-for-parameter

    @mpi.exchange(receive=True, send=True)
    def tracking_request(self, _sender_id, body):
        """Summarise tracked objects for the camera gateway."""
        self.logger.info("Received request | " + format_log_kv(request=body))
        labels = [track["label"] for track in body["tracks"]]
        return "CameraGatewayService", {
            "response_type": "analytics_result",
            "frame_id": body["frame_id"],
            "stream_id": body["stream_id"],
            "object_count": len(body["tracks"]),
            "summary": ", ".join(labels),
        }
