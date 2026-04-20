"""MPI workflow for telemetry capture."""

from eclypse.remote.communication import mpi
from eclypse.remote.service import Service
from eclypse.utils import format_log_kv


class SensorService(Service):
    """Generate telemetry windows and start the anomaly pipeline."""

    def __init__(self, service_id: str, store_step: bool = False):
        """Initialise the sensor with a rolling telemetry window counter."""
        super().__init__(service_id, store_step=store_step)
        self.window_id = 0

    async def step(self):
        """Create the next telemetry window and wait for the alert result."""
        self.window_id += 1
        await self.capture_window()
        response = await self.mpi.recv()
        self.logger.info("Received response | " + format_log_kv(response=response))
        return response

    @mpi.exchange(send=True)
    def capture_window(self):
        """Send a synthetic telemetry window to the feature extractor."""
        return "FeatureService", {
            "request_type": "extract_features",
            "window_id": self.window_id,
            "samples": [0.8, 1.2, 4.5],
        }
