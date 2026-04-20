"""REST workflow for the camera gateway service."""

from eclypse.remote.service import Service
from eclypse.utils import format_log_kv


class CameraGatewayService(Service):
    """Entry-point service that starts the video analytics pipeline."""

    def __init__(self, service_id: str, store_step: bool = False):
        """Initialise the gateway with a rolling frame counter."""
        super().__init__(
            service_id,
            communication_interface="rest",
            store_step=store_step,
        )
        self.frame_id = 0

    async def step(self):
        """Drive one frame through the REST analytics pipeline."""
        self.frame_id += 1
        detection_r = await self.rest.post(
            "DetectionService/detect",
            frame_id=self.frame_id,
            stream_id="camera-a",
            objects=["person", "forklift"],
        )
        self.logger.info(
            "Received response | "
            + format_log_kv(source="DetectionService", body=detection_r.body)
        )
        tracking_r = await self.rest.post(
            "TrackingService/track",
            frame_id=self.frame_id,
            stream_id="camera-a",
            detections=detection_r.body["detections"],
        )
        self.logger.info(
            "Received response | "
            + format_log_kv(source="TrackingService", body=tracking_r.body)
        )
        analytics_r = await self.rest.post(
            "AnalyticsService/analyse",
            frame_id=self.frame_id,
            stream_id="camera-a",
            tracks=tracking_r.body["tracks"],
        )
        self.logger.info(
            "Received response | "
            + format_log_kv(source="AnalyticsService", body=analytics_r.body)
        )
        return analytics_r
