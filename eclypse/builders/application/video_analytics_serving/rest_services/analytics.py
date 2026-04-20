"""REST endpoints for the analytics service."""

from eclypse.remote.communication import rest
from eclypse.remote.service import RESTService
from eclypse.utils import format_log_kv


class AnalyticsService(RESTService):
    """Aggregate tracked events into a compact result."""

    @rest.endpoint("/analyse", "POST")
    def analyse(self, frame_id: int, stream_id: str, tracks: list[dict], **_):
        """Summarise tracked objects for the requested frame."""
        self.logger.info(
            "Received request | "
            + format_log_kv(frame_id=frame_id, stream_id=stream_id, tracks=tracks)
        )
        labels = [track["label"] for track in tracks]
        return 200, {
            "frame_id": frame_id,
            "stream_id": stream_id,
            "object_count": len(tracks),
            "summary": ", ".join(labels),
        }
