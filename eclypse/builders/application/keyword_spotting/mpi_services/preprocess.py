"""MPI workflow for audio preprocessing."""

from eclypse.remote.communication import mpi
from eclypse.remote.service import Service
from eclypse.utils import format_log_kv


class PreprocessService(Service):
    """Turn raw samples into simple features."""

    async def step(self):
        """Handle the next raw audio window emitted by the sensor."""
        await self.sensor_request()  # pylint: disable=no-value-for-parameter

    @mpi.exchange(receive=True, send=True)
    def sensor_request(self, _sender_id, body):
        """Convert raw audio samples into a simple feature vector."""
        self.logger.info("Received request | " + format_log_kv(request=body))
        features = [sample * 10 for sample in body["samples"]]
        return "InferenceService", {
            "request_type": "run_inference",
            "window_id": body["window_id"],
            "features": features,
        }
