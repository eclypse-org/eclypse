"""MPI workflow for the tracking service."""

from eclypse.remote.communication import mpi
from eclypse.remote.service import Service
from eclypse.utils import format_log_kv


class TrackingService(Service):
    """Track detected objects across frames."""

    async def step(self):
        """Handle the next detection payload produced by the detector."""
        await self.detection_request()  # pylint: disable=no-value-for-parameter

    @mpi.exchange(receive=True, send=True)
    def detection_request(self, _sender_id, body):
        """Assign synthetic track identifiers to each detected object."""
        self.logger.info("Received request | " + format_log_kv(request=body))
        tracks = [
            {"label": label, "track_id": index + 1}
            for index, label in enumerate(body["detections"])
        ]
        return "AnalyticsService", {
            "request_type": "aggregate_events",
            "frame_id": body["frame_id"],
            "stream_id": body["stream_id"],
            "tracks": tracks,
        }
