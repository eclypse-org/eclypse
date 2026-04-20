"""REST workflow for telemetry capture."""

from eclypse.remote.service import Service
from eclypse.utils import format_log_kv


class SensorService(Service):
    """Generate telemetry windows and start the anomaly pipeline."""

    def __init__(self, service_id: str, store_step: bool = False):
        """Initialise the sensor with a rolling telemetry window counter."""
        super().__init__(
            service_id,
            communication_interface="rest",
            store_step=store_step,
        )
        self.window_id = 0

    async def step(self):
        """Drive one telemetry window through the REST inference pipeline."""
        self.window_id += 1
        feature_r = await self.rest.post(
            "FeatureService/features",
            window_id=self.window_id,
            samples=[0.8, 1.2, 4.5],
        )
        self.logger.info(
            "Received response | "
            + format_log_kv(source="FeatureService", body=feature_r.body)
        )
        inference_r = await self.rest.post(
            "InferenceService/score",
            window_id=self.window_id,
            features=feature_r.body["features"],
        )
        self.logger.info(
            "Received response | "
            + format_log_kv(source="InferenceService", body=inference_r.body)
        )
        alert_r = await self.rest.post(
            "AlertService/alert",
            window_id=self.window_id,
            score=inference_r.body["score"],
        )
        self.logger.info(
            "Received response | "
            + format_log_kv(source="AlertService", body=alert_r.body)
        )
        return alert_r
