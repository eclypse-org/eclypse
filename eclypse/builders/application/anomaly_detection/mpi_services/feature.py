"""MPI workflow for feature extraction."""

from eclypse.remote.communication import mpi
from eclypse.remote.service import Service
from eclypse.utils import format_log_kv


class FeatureService(Service):
    """Extract simple features from telemetry."""

    async def step(self):
        """Handle the next telemetry window produced by the sensor."""
        await self.sensor_request()  # pylint: disable=no-value-for-parameter

    @mpi.exchange(receive=True, send=True)
    def sensor_request(self, _sender_id, body):
        """Compute compact statistics for the received telemetry samples."""
        self.logger.info("Received request | " + format_log_kv(request=body))
        max_sample = max(body["samples"])
        mean_sample = sum(body["samples"]) / len(body["samples"])
        return "InferenceService", {
            "request_type": "score_window",
            "window_id": body["window_id"],
            "features": {"max": max_sample, "mean": mean_sample},
        }
