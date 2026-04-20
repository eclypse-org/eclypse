"""MPI workflow for audio window capture."""

from eclypse.remote.communication import mpi
from eclypse.remote.service import Service
from eclypse.utils import format_log_kv


class SensorService(Service):
    """Generate audio windows and start the spotting pipeline."""

    def __init__(self, service_id: str, store_step: bool = False):
        """Initialise the sensor with a rolling audio window counter."""
        super().__init__(service_id, store_step=store_step)
        self.window_id = 0

    async def step(self):
        """Create the next audio window and wait for the command response."""
        self.window_id += 1
        await self.capture_window()
        response = await self.mpi.recv()
        self.logger.info("Received response | " + format_log_kv(response=response))
        return response

    @mpi.exchange(send=True)
    def capture_window(self):
        """Send a synthetic audio window to the preprocessing service."""
        return "PreprocessService", {
            "request_type": "preprocess_audio",
            "window_id": self.window_id,
            "samples": [0.1, 0.3, 0.2],
        }
