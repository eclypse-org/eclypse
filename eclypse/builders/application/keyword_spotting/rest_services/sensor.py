"""REST workflow for audio window capture."""

from eclypse.remote.service import Service
from eclypse.utils import format_log_kv


class SensorService(Service):
    """Generate audio windows and start the spotting pipeline."""

    def __init__(self, service_id: str, store_step: bool = False):
        """Initialise the sensor with a rolling audio window counter."""
        super().__init__(
            service_id,
            communication_interface="rest",
            store_step=store_step,
        )
        self.window_id = 0

    async def step(self):
        """Drive one audio window through the REST spotting pipeline."""
        self.window_id += 1
        preprocess_r = await self.rest.post(
            "PreprocessService/preprocess",
            window_id=self.window_id,
            samples=[0.1, 0.3, 0.2],
        )
        self.logger.info(
            "Received response | "
            + format_log_kv(source="PreprocessService", body=preprocess_r.body)
        )
        inference_r = await self.rest.post(
            "InferenceService/infer",
            window_id=self.window_id,
            features=preprocess_r.body["features"],
        )
        self.logger.info(
            "Received response | "
            + format_log_kv(source="InferenceService", body=inference_r.body)
        )
        action_r = await self.rest.post(
            "ActionService/action",
            window_id=self.window_id,
            keyword=inference_r.body["keyword"],
        )
        self.logger.info(
            "Received response | "
            + format_log_kv(source="ActionService", body=action_r.body)
        )
        return action_r
