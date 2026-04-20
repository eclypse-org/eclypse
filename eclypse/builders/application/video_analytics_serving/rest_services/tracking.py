"""REST endpoints for the tracking service."""

from eclypse.remote.communication import rest
from eclypse.remote.service import RESTService
from eclypse.utils import format_log_kv


class TrackingService(RESTService):
    """Track detected objects across frames."""

    @rest.endpoint("/track", "POST")
    def track(self, frame_id: int, stream_id: str, detections: list[str], **_):
        """Assign synthetic track identifiers to each detected object."""
        self.logger.info(
            "Received request | "
            + format_log_kv(
                frame_id=frame_id,
                stream_id=stream_id,
                detections=detections,
            )
        )
        return 200, {
            "frame_id": frame_id,
            "stream_id": stream_id,
            "tracks": [
                {"label": label, "track_id": index + 1}
                for index, label in enumerate(detections)
            ],
        }
