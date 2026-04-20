"""MPI workflow for acting on a detected keyword."""

from eclypse.remote.communication import mpi
from eclypse.remote.service import Service
from eclypse.utils import format_log_kv


class ActionService(Service):
    """Convert a keyword into a final command response."""

    async def step(self):
        """Handle the next inference result produced by the keyword model."""
        await self.inference_request()  # pylint: disable=no-value-for-parameter

    @mpi.exchange(receive=True, send=True)
    def inference_request(self, _sender_id, body):
        """Map the detected keyword to a command for the sensor."""
        self.logger.info("Received request | " + format_log_kv(request=body))
        return "SensorService", {
            "response_type": "keyword_response",
            "window_id": body["window_id"],
            "command": "wake" if body["keyword"] == "eclypse" else "idle",
        }
