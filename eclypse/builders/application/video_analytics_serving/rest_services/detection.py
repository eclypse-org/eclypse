"""REST endpoints for the detection service."""

from eclypse.remote.communication import rest
from eclypse.remote.service import RESTService
from eclypse.utils import format_log_kv


class DetectionService(RESTService):
    """Detect objects in incoming frames."""

    @rest.endpoint("/detect", "POST")
    def detect(self, frame_id: int, stream_id: str, objects: list[str], **_):
        """Return the objects detected in the incoming frame."""
        self.logger.info(
            "Received request | "
            + format_log_kv(frame_id=frame_id, stream_id=stream_id, objects=objects)
        )
        return 200, {
            "frame_id": frame_id,
            "stream_id": stream_id,
            "detections": objects,
        }
